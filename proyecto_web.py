import streamlit as st
import pandas as pd
from datetime import datetime
import holidays

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
    st.session_state["registro_horas"] = {}  # Guarda todas las horas ingresadas
if "fecha_anterior" not in st.session_state:
    st.session_state["fecha_anterior"] = None
if "horas_extra_temp" not in st.session_state:
    st.session_state["horas_extra_temp"] = None

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
# ESTILOS: fondo dinámico y blur en contenedor
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

    # ----------------------
    # SELECCIÓN DE FECHA
    # ----------------------
    fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)", value=None)

    # Guardar automáticamente la hora extra de la fecha anterior
    if st.session_state["fecha_anterior"] and st.session_state.get("horas_extra_temp") is not None:
        st.session_state["registro_horas"][st.session_state["fecha_anterior"]] = st.session_state["horas_extra_temp"]

    # Inicializar horas_extra vacío por cada fecha
    horas_extra = None
    if fecha_seleccionada:
        fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")

        # Calcular feriados automáticamente
        peru_feriados = holidays.Peru(years=fecha_seleccionada.year)
        feriados = [f.strftime("%Y-%m-%d") for f in peru_feriados.keys()]

        horas_extra = st.number_input(
            f"Horas extra del día seleccionado:",
            min_value=0,
            step=1,
            format="%d",
            value=None,
            key="horas_extra_temp"
        )

        st.session_state["fecha_anterior"] = fecha_str

    # ----------------------
    # BOTONES
    # ----------------------
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Calcular Horas Extra"):
            # Guardar la última fecha antes de calcular
            if st.session_state["fecha_anterior"] and st.session_state.get("horas_extra_temp") is not None:
                st.session_state["registro_horas"][st.session_state["fecha_anterior"]] = st.session_state["horas_extra_temp"]

            if nombre_empleado and sueldo_mensual:
                valor_hora = round(sueldo_mensual / (8 * 5 * 4.33), 2)
                registros = []

                for fecha_str, horas in st.session_state["registro_horas"].items():
                    if horas:
                        fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
                        dia_semana = fecha_dt.weekday()  # 0=lunes, 6=domingo
                        es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (fecha_str in feriados)

                        # Lógica de horas extra
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

                    # Guardar Excel correctamente
                    df.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
                    st.success("Reporte guardado como 'HorasExtra_Mes_Reporte.xlsx'")
                else:
                    st.info("No se ingresaron horas extra.")
            else:
                st.warning("⚠️ Complete todos los campos.")

    with col2:
        if st.button("Limpiar HRS EXT."):
            st.session_state["registro_horas"] = {}
            st.session_state["horas_extra_temp"] = None
            st.session_state["fecha_anterior"] = None
            st.success("✅ Historial de horas extra limpiado. Todos los campos vacíos.")

