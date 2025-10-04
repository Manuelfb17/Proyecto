import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import os

# ==============================
# Archivo para guardar horas
# ==============================
ARCHIVO_HORAS = "horas_guardadas.xlsx"

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
    st.session_state["registro_horas"] = {}  # Guarda todas las horas ingresadas

# ==============================
# Cargar datos guardados si existen
# ==============================
if os.path.exists(ARCHIVO_HORAS):
    df_guardado = pd.read_excel(ARCHIVO_HORAS)
    # Convertir a diccionario {fecha: horas}
    st.session_state["registro_horas"].update(dict(zip(df_guardado['Fecha'], df_guardado['Horas Extra'])))

# ==============================
# ICONO Y NOMBRE PARA IOS (PWA)
# ==============================
st.markdown("""
<meta name="apple-mobile-web-app-title" content="Horas Extra Marco">
<link rel="apple-touch-icon" sizes="180x180" href="https://i.postimg.cc/7PjfgKkz/marco-peruana.png">
<meta name="apple-mobile-web-app-capable" content="yes">
""", unsafe_allow_html=True)

# ----------------------
# CONFIGURACIÓN DE LA PÁGINA
# ----------------------
st.set_page_config(
    page_title="Registro de Horas Extra",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# ESTILOS: fondo dinámico difuminado
# ==============================
st.markdown(
    """
    <style>
    .stApp {
        background: 
            linear-gradient(to bottom, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0) 40%),
            url('https://www.marco.com.pe/wp-content/uploads/2021/01/marco-7.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .contenido {
        margin-top: 20px;
        padding: 20px;
        border-radius: 10px;
        backdrop-filter: blur(8px);
        background-color: rgba(255,255,255,0.2);
    }
    .block-container {
        padding-top: 0rem;
    }
    .campo-datos {
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True
)

# ==============================
# CONTENIDO DE LA APP
# ==============================
with st.container():
    st.markdown('<div class="contenido"></div>', unsafe_allow_html=True)

    # ----------------------
    # BLOQUE DE DATOS GENERALES
    # ----------------------
    st.subheader("REGISTRO DE HORAS EXTRA")
    nombre_empleado = st.text_input("Ingrese su nombre", value="")
    sueldo_mensual = st.number_input(
        "Ingrese su sueldo mensual (S/):",
        min_value=0,
        step=100,
        format="%d",
        value=None
    )
    fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)")

    # ----------------------
    # BLOQUE HORAS EXTRA
    # ----------------------
    horas_extra = 0
    if fecha_seleccionada:
        fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")
        # Mostrar horas previamente guardadas para esa fecha
        horas_extra = st.session_state["registro_horas"].get(fecha_str, 0)
        horas_extra = st.number_input(
            f"Horas extra del día seleccionado:",
            min_value=0,
            step=1,
            format="%d",
            value=horas_extra
        )
        # Guardar automáticamente en session_state
        st.session_state["registro_horas"][fecha_str] = horas_extra

    # ----------------------
    # BOTÓN LIMPIAR HORAS EXTRA
    # ----------------------
    if st.button("Limpiar Hrs. Ext."):
        st.session_state["registro_horas"].clear()
        # Borrar archivo guardado
        if os.path.exists(ARCHIVO_HORAS):
            os.remove(ARCHIVO_HORAS)
        st.experimental_rerun()

    # ----------------------
    # BOTÓN CALCULAR Y TABLA
    # ----------------------
    if st.button("Calcular Horas Extra"):
        if nombre_empleado and sueldo_mensual:
            valor_hora = round(sueldo_mensual / (8 * 5 * 4.33), 2)
            registros = []

            # Calcular feriados de Perú
            anio_actual = datetime.now().year
            peru_feriados = holidays.Peru(years=anio_actual)
            feriados = [fecha.strftime("%Y-%m-%d") for fecha in peru_feriados.keys()]

            for fecha_str, horas in st.session_state["registro_horas"].items():
                if horas:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    dia_semana = fecha.weekday()
                    es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (fecha_str in feriados)

                    if es_domingo_o_feriado:
                        pago = round(horas * valor_hora * 2, 2)
                    else:
                        if horas <= 2:
                            pago = round(horas * valor_hora * 0.25, 2)
                        else:
                            pago = round(2*valor_hora*0.25 + (horas-2)*valor_hora*0.35, 2)

                    registros.append({
                        "Empleado": nombre_empleado,
                        "Fecha": fecha_str,
                        "Horas Extra": horas,
                        "Pago Extra (S/)": pago
                    })

            if registros:
                df = pd.DataFrame(registros)
                st.subheader("📊 Reporte de Horas Extra")
                st.dataframe(df)
                st.write("💰 **Total de horas extra (S/):**", df["Pago Extra (S/)"].sum())

                # Guardar Excel con columnas separadas
                df.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
                # Guardar historial permanente
                df_guardado = pd.DataFrame([
                    {"Fecha": k, "Horas Extra": v} for k, v in st.session_state["registro_horas"].items()
                ])
                df_guardado.to_excel(ARCHIVO_HORAS, index=False)

                # Botón de descarga
                st.download_button(
                    label="📥 Descargar Reporte Excel",
                    data=df.to_excel(index=False, engine='openpyxl'),
                    file_name="HorasExtra_Mes_Reporte.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No se ingresaron horas extra.")
        else:
            st.warning("⚠️ Complete todos los campos.")
