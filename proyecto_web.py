import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import holidays

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
st.write("Complete los datos para calcular el pago de sus horas extra.")

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
    # Nombre del empleado
    nombre_empleado = st.text_input("Ingrese su nombre", value="")

    # Sueldo mensual
    sueldo_mensual = st.number_input(
        "Ingrese su sueldo mensual (S/):",
        min_value=0,
        step=100,
        format="%d",
        value=None
    )

    # Selector de fecha (para mes y año)
    fecha_seleccionada = st.date_input("Seleccione mes y año:", value=None)

    horas_dict = {}
    if fecha_seleccionada:
        anio = fecha_seleccionada.year
        mes = fecha_seleccionada.month

        # Obtener feriados automáticamente según el año
        peru_feriados = holidays.Peru(years=anio)
        feriados = [fecha.strftime("%Y-%m-%d") for fecha in peru_feriados.keys()]

        # Generar inputs para cada día del mes seleccionado
        num_dias = calendar.monthrange(anio, mes)[1]
        for dia in range(1, num_dias + 1):
            fecha = datetime(anio, mes, dia)
            fecha_str = fecha.strftime("%Y-%m-%d")
            horas_dict[fecha_str] = st.number_input(
                f"{fecha_str} - Horas extra:",
                min_value=0,
                step=1,
                format="%d",
                value=None,
                key=fecha_str
            )

    submitted = st.form_submit_button("Calcular Horas Extra")

# ----------------------
# PROCESAMIENTO
# ----------------------
if submitted:
    if nombre_empleado and sueldo_mensual and fecha_seleccionada:
        # Valor hora basado en 8h diarias, 5 días por semana, 4.33 semanas promedio
        valor_hora = round(sueldo_mensual / (8 * 5 * 4.33), 2)

        registros = []
        for fecha_str, horas_extra in horas_dict.items():
            if horas_extra:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                dia_semana = fecha.weekday()  # 0=lunes, 6=domingo
                es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (fecha_str in feriados)
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
