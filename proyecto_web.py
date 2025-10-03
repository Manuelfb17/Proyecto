import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

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
# BANNER SUPERIOR (desliza con scroll)
# ----------------------
st.markdown(
    """
    <style>
    .banner-top {
        position: relative; 
        top: 0;
        left: 0;
        width: 100%;
        overflow: hidden;
        background-color: white;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    }
    .banner-top img {
        width: 100%;
        height: 280px;
        object-fit: cover;
    }
    .content {
        margin-top: 20px;
    }
    </style>
    <div class="banner-top">
        <img src="https://www.marco.com.pe/wp-content/uploads/2021/01/marco-7.jpg" alt="Marco Peru Banner">
    </div>
    <div class="content">
    """,
    unsafe_allow_html=True
)

# ----------------------
# CONTENIDO DE LA APP
# ----------------------
st.title("Registro de Horas Extra")
st.write("Completa los datos para calcular el pago de tus horas extra.")

# lista de feriados en Perú 2025
feriados = [
    "2025-01-01", "2025-04-18", "2025-05-01", "2025-07-28",
    "2025-07-29", "2025-08-30", "2025-10-08", "2025-12-08", "2025-12-25"
]

def convertir_hora_simple(hora_simple):
    hora_simple = hora_simple.strip().lower()
    if "am" in hora_simple:
        hora = int(hora_simple.replace("am", ""))
        if hora == 12:
            hora = 0
    elif "pm" in hora_simple:
        hora = int(hora_simple.replace("pm", ""))
        if hora != 12:
            hora += 12
    else:
        hora = int(hora_simple)
    return f"{hora:02d}:00"

def calcular_pago_horas_extra(horas_extra, valor_hora, es_domingo_o_feriado):
    if es_domingo_o_feriado:
        return round(horas_extra * valor_hora * 2, 2)
    else:
        if horas_extra <= 2:
            return round(horas_extra * valor_hora * 0.25, 2)
        else:
            extra = 2 * valor_hora * 0.25 + (horas_extra - 2) * valor_hora * 0.35
            return round(extra, 2)

# ----------------------
# FORMULARIO DE ENTRADA
# ----------------------
nombre_empleado = st.text_input("Ingrese su nombre")
sueldo_mensual = st.number_input("Ingrese su sueldo mensual (S/):", min_value=0.0, step=10.0)
entrada_normal = st.text_input("Ingrese hora de entrada (ej: 8am, 10pm)")
salida_normal = st.text_input("Ingrese hora de salida (ej: 5pm, 10pm)")

anio = st.number_input("Ingrese el año (YYYY):", min_value=2000, max_value=2100, value=datetime.today().year)
mes = st.number_input("Ingrese el mes (1-12):", min_value=1, max_value=12, value=datetime.today().month)

# ----------------------
# CAMPOS DE HORAS EXTRA (SIEMPRE VISIBLES)
# ----------------------
num_dias = calendar.monthrange(anio, mes)[1]
if "horas_extra" not in st.session_state:
    st.session_state.horas_extra = {dia: 0.0 for dia in range(1, num_dias + 1)}

st.subheader("🕒 Registro diario de horas extra")
for dia in range(1, num_dias + 1):
    fecha = datetime(anio, mes, dia).strftime("%Y-%m-%d")
    st.session_state.horas_extra[dia] = st.number_input(
        f"{fecha} - Horas extra:",
        min_value=0.0,
        step=1.0,
        key=f"dia_{dia}",
        value=st.session_state.horas_extra.get(dia, 0.0)
    )

# ----------------------
# BOTÓN DE CÁLCULO
# ----------------------
if st.button("Calcular Horas Extra"):
    if nombre_empleado and sueldo_mensual > 0 and entrada_normal and salida_normal:
        hora_entrada = datetime.strptime(convertir_hora_simple(entrada_normal), "%H:%M")
        hora_salida = datetime.strptime(convertir_hora_simple(salida_normal), "%H:%M")
        if hora_salida < hora_entrada:
            hora_salida += timedelta(days=1)

        duracion_jornada = (hora_salida - hora_entrada).seconds / 3600
        valor_hora = round(sueldo_mensual / (duracion_jornada * 5 * 4.33), 2)

        registros = []
        for dia, horas_extra in st.session_state.horas_extra.items():
            if horas_extra > 0:
                fecha = datetime(anio, mes, dia)
                fecha_str = fecha.strftime("%Y-%m-%d")
                dia_semana = fecha.weekday()
                es_domingo_o_feriado = (dia_semana == 6) or (fecha_str in feriados)

                pago = calcular_pago_horas_extra(horas_extra, valor_hora, es_domingo_o_feriado)
                registros.append({
                    "Empleado": nombre_empleado,
                    "Fecha": fecha_str,
                    "Horas Extra": horas_extra,
                    "Pago Extra (S/)": pago
                })

        if registros:
            df = pd.DataFrame(registros)
            st.subheader("📊 Reporte de Horas Extra del Mes")
            st.dataframe(df)
            st.write("💰 **Total de horas extra (S/):**", df["Pago Extra (S/)"].sum())

            df.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
            st.success("Reporte guardado como 'HorasExtra_Mes_Reporte.xlsx'")
    else:
        st.warning("⚠️ Complete todos los campos para calcular.")

# ----------------------
# Cerrar content
# ----------------------
st.markdown("</div>", unsafe_allow_html=True)
