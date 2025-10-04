import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ==============================
# ICONO Y NOMBRE PARA IOS (PWA)
# ==============================
st.markdown("""
<!-- Nombre que aparecerá en la pantalla de inicio del iPhone -->
<meta name="apple-mobile-web-app-title" content="Horas Extra Marco">

<!-- Icono que se usará en la pantalla de inicio -->
<link rel="apple-touch-icon" sizes="180x180" href="https://i.postimg.cc/7PjfgKkz/marco-peruana.png">

<!-- Permite que la app se abra en pantalla completa -->
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
# BANNER SUPERIOR (se desliza con el scroll)
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
    </style>
    <div class="banner">
        <img src="https://i.postimg.cc/7PjfgKkz/marco-peruana.png" alt="Marco Peru Banner">
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------
# CONTENIDO DE LA APP
# ----------------------
st.title("Registro de Horas Extra")

# lista de feriados en Perú 2025
feriados = [
    "2025-01-01", "2025-04-18", "2025-05-01", "2025-07-28",
    "2025-07-29", "2025-08-30", "2025-10-08", "2025-12-08", "2025-12-25"
]

# ----------------------
# FUNCIONES
# ----------------------
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
# FORMULARIO PRINCIPAL
# ----------------------
with st.form("form_horas_extra"):
    nombre_empleado = st.text_input("Ingrese su nombre")
    sueldo_mensual = st.number_input("Ingrese su sueldo mensual (S/):", min_value=0.0, step=10.0)

    anio = st.number_input("Ingrese el año):", min_value=2000, max_value=2100, value=datetime.today().year)
    mes = st.number_input("Ingrese el mes (1-12):", min_value=1, max_value=12, value=datetime.today().month)

    st.markdown("---")
    st.subheader("Ingrese las horas extra de cada día:")

    num_dias = calendar.monthrange(anio, mes)[1]
    horas_dict = {}

    for dia in range(1, num_dias + 1):
        fecha = datetime(anio, mes, dia)
        fecha_str = fecha.strftime("%Y-%m-%d")
        horas_dict[fecha_str] = st.number_input(f"{fecha_str} - Horas extra:", min_value=0.0, step=1.0, key=fecha_str)

    submitted = st.form_submit_button("Calcular Horas Extra")

# ----------------------
# PROCESAMIENTO
# ----------------------
if submitted:
    if nombre_empleado and sueldo_mensual > 0:
        # Valor de la hora basado en 8 horas diarias, 5 días por semana, 4.33 semanas promedio por mes
        valor_hora = round(sueldo_mensual / (8 * 5 * 4.33), 2)

        registros = []
        for fecha_str, horas_extra in horas_dict.items():
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            dia_semana = fecha.weekday()
            es_domingo_o_feriado = (dia_semana >= 5) or (fecha_str in feriados)  # sábado/domingo o feriado

            if horas_extra > 0:
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
            st.info("No se ingresaron horas extra en ningún día.")
    else:
        st.warning("⚠️ Complete todos los campos para calcular.")
