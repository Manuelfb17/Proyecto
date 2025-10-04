import streamlit as st
import pandas as pd
from datetime import datetime
import holidays

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
    st.session_state["registro_horas"] = {}  # Guarda todas las horas ingresadas

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

# ----------------------
# BANNER SUPERIOR
# ----------------------
st.markdown(
    """
    <style>
    .banner {
        width: 100%;
        overflow: hidden;
        background-color: white;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .banner img {
        width: 100%;
        height: 300px;
        object-fit: cover;
        display: block;
    }
    .campo-datos {
        margin-bottom: 20px;
    }
    </style>
    <div class="banner">
        <img src="https://i.postimg.cc/7PjfgKkz/marco-peruana.png" alt="Marco Peru Banner">
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------
# BLOQUE DE DATOS GENERALES
# ----------------------
st.subheader("REGISTRO DE HORAS EXTRA")
with st.container():
    st.markdown("<div class='campo-datos'></div>", unsafe_allow_html=True)
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

    st.subheader("Ingrese las horas extra del día seleccionado")
    with st.container():
        st.markdown("<div class='campo-datos'></div>", unsafe_allow_html=True)
        horas_extra = st.number_input(
            f"Horas extra para {fecha_str}:",
            min_value=0,
            step=1,
            format="%d",
            value=st.session_state["registro_horas"].get(fecha_str, None)
        )
        # Guardar automáticamente en session_state
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
                dia_semana = fecha.weekday()  # 0=lunes, 6=domingo
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
            df.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
            st.success("Reporte guardado como 'HorasExtra_Mes_Reporte.xlsx'")
        else:
            st.info("No se ingresaron horas extra.")
    else:
        st.warning("⚠️ Complete todos los campos.")
