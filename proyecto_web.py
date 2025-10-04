import streamlit as st
import pandas as pd
from datetime import datetime
import holidays

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
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
# ESTILOS: fondo dinámico + header fijo
# ==============================
st.markdown(
    """
    <style>
    /* Fondo dinámico */
    .stApp {
        background-image: url('https://www.marco.com.pe/wp-content/uploads/2021/01/marco-7.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Header fijo con fondo blanco */
    .header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 80px;
        background-color: white;
        display: flex;
        align-items: center;
        padding-left: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        z-index: 9999;
    }

    /* Contenedor de la app debajo del header */
    .contenido {
        margin-top: 100px;
        padding: 20px;
        background-color: rgba(255,255,255,0.9);
        border-radius: 10px;
    }

    .campo-datos {
        margin-bottom: 20px;
    }
    </style>

    <!-- Header fijo (sin logo) -->
    <div class="header"></div>
""", unsafe_allow_html=True)

# ==============================
# CONTENIDO DE LA APP
# ==============================
st.markdown('<div class="contenido">', unsafe_allow_html=True)

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
fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)", value=None)

# ----------------------
# BLOQUE HORAS EXTRA
# ----------------------
if fecha_seleccionada:
    anio = fecha_seleccionada.year
    mes = fecha_seleccionada.month
    dia = fecha_seleccionada.day
    fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")

    # Calcular feriados automáticamente
    peru_feriados = holidays.Peru(years=anio)
    feriados = [fecha.strftime("%Y-%m-%d") for fecha in peru_feriados.keys()]

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader(f"Ingrese las horas extra para {fecha_str}")
    horas_extra = st.number_input(
        f"Horas extra del día seleccionado:",
        min_value=0,
        step=1,
        format="%d",
        value=st.session_state["registro_horas"].get(fecha_str, None)
    )
    st.session_state["registro_horas"][fecha_str] = horas_extra

# ----------------------
# BOTÓN CALCULAR Y TABLA
# ----------------------
if st.button("Calcular Horas Extra"):
    if nombre_empleado and sueldo_mensual:
        valor_hora = round(sueldo_mensual / (8 * 5 * 4.33), 2)
        registros = []

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
            df.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
            st.success("Reporte guardado como 'HorasExtra_Mes_Reporte.xlsx'")
        else:
            st.info("No se ingresaron horas extra.")
    else:
        st.warning("⚠️ Complete todos los campos.")

st.markdown('</div>', unsafe_allow_html=True)
