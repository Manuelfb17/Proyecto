import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import os

# ==============================
# Archivo para guardar los datos
# ==============================
archivo_datos = "registro_horas.csv"

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
    # Cargar desde CSV si existe
    if os.path.exists(archivo_datos):
        df_guardado = pd.read_csv(archivo_datos)
        # Convertir a diccionario {fecha: horas}
        registro_horas = {}
        for _, row in df_guardado.iterrows():
            registro_horas[row["Fecha"]] = row["Horas Extra"]
        st.session_state["registro_horas"] = registro_horas
    else:
        st.session_state["registro_horas"] = {}

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
st.markdown("""
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
    margin-top: 0px !important;
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
""", unsafe_allow_html=True)

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
    horas_extra = 0  # Valor por defecto
    if fecha_seleccionada:
        fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")

        # Si ya hay horas guardadas para esa fecha, mostrarlo
        if fecha_str in st.session_state["registro_horas"]:
            horas_extra_valor = st.session_state["registro_horas"][fecha_str]
        else:
            horas_extra_valor = 0

        horas_extra = st.number_input(
            f"Horas extra del día {fecha_str}:",
            min_value=0,
            step=1,
            format="%d",
            value=0
        )

    # ----------------------
    # BOTÓN LIMPIAR HISTORIAL
    # ----------------------
    if st.button("Limpiar HRS EXT."):
        st.session_state["registro_horas"] = {}
        if os.path.exists(archivo_datos):
            os.remove(archivo_datos)
        st.success("Historial de horas extra limpiado!")

    # ----------------------
    # BOTÓN CALCULAR Y TABLA
    # ----------------------
    if st.button("Calcular Horas Extra"):
        if nombre_empleado and sueldo_mensual:
            if fecha_seleccionada and horas_extra > 0:
                # Guardar horas en la sesión
                st.session_state["registro_horas"][fecha_str] = horas_extra

                # Guardar en CSV para mantener persistencia
                df_guardar = pd.DataFrame([
                    {"Empleado": nombre_empleado,
                     "Fecha": f,
                     "Horas Extra": h,
                     "Pago Extra (S/)": 0}  # se calculará después
                    for f, h in st.session_state["registro_horas"].items()
                ])
                df_guardar.to_csv(archivo_datos, index=False)

            registros = []
            anio = fecha_seleccionada.year if fecha_seleccionada else datetime.today().year
            peru_feriados = holidays.Peru(years=anio)
            feriados = [fecha.strftime("%Y-%m-%d") for fecha in peru_feriados.keys()]

            for f, h in st.session_state["registro_horas"].items():
                fecha_obj = datetime.strptime(f, "%Y-%m-%d")
                dia_semana = fecha_obj.weekday()
                es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (f in feriados)

                if es_domingo_o_feriado:
                    pago = round(h * (sueldo_mensual / (8*5*4.33)) * 2, 2)
                else:
                    valor_hora = round(sueldo_mensual / (8*5*4.33), 2)
                    if h <= 2:
                        pago = round(h * valor_hora * 0.25, 2)
                    else:
                        pago = round(2*valor_hora*0.25 + (h-2)*valor_hora*0.35, 2)

                registros.append({
                    "Empleado": nombre_empleado,
                    "Fecha": f,
                    "Horas Extra": h,
                    "Pago Extra (S/)": pago
                })

            if registros:
                df = pd.DataFrame(registros)
                st.subheader("📊 Reporte de Horas Extra")
                st.dataframe(df)

                # Botón para descargar Excel
                st.download_button(
                    label="📥 Descargar Excel",
                    data=df.to_excel(index=False, engine='openpyxl'),
                    file_name="HorasExtra_Mes_Reporte.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("⚠️ Complete todos los campos.")
