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
    layout="wide",  # usar toda la pantalla
    initial_sidebar_state="expanded"
)

# ----------------------
# BANNER SUPERIOR FIJO (logo Marco Peruana)
# ----------------------
st.markdown(
    """
    <style>
    .banner-fixed {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 999;
        background-color: white; /* fondo blanco para el logo */
        text-align: center;
        padding: 5px 0;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    }
    .banner-fixed img {
        width: 100%;
        height: auto;
        max-height: 160px;   /* ajusta el alto máximo del logo */
        object-fit: contain; /* muestra el logo completo */
    }
    .content {
        margin-top: 180px;  /* espacio suficiente debajo del banner */
    }
    </style>
    <div class="banner-fixed">
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
    """Convierte una hora en formato 8am/5pm a formato 24h"""
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
    """Calcula el pago según si es domingo/feriado o día normal"""
    if es_domingo_o_feriado:
        return round(horas_extra * valor_hora * 2, 2)  # 200%
    else:
        if horas_extra <= 2:
            return round(horas_extra * valor_hora * 0.25, 2)
        else:
            extra = 2 * valor_hora * 0.25 + (horas_extra - 2) * valor_hora * 0.35
            return round(extra, 2)

# Entradas del usuario
nombre_empleado = st.text_input("Ingrese su nombre")
sueldo_mensual = st.number_input("Ingrese su sueldo mensual (S/):", min_value=0.0, step=10.0)
entrada_normal = st.text_input("Ingrese hora de entrada (ej: 8am, 10pm)")
salida_normal = st.text_input("Ingrese hora de salida (ej: 5pm, 10pm)")

anio = st.number_input("Ingrese el año (YYYY):", min_value=2000, max_value=2100, value=datetime.today().year)
mes = st.number_input("Ingrese el mes (1-12):", min_value=1, max_value=12, value=datetime.today().month)

# Botón de cálculo
if st.button("Calcular Horas Extra"):
    if nombre_empleado and sueldo_mensual > 0 and entrada_normal and salida_normal:
        # Calcular valor hora
        hora_entrada = datetime.strptime(convertir_hora_simple(entrada_normal), "%H:%M")
        hora_salida = datetime.strptime(convertir_hora_simple(salida_normal), "%H:%M")
        if hora_salida < hora_entrada:
            hora_salida += timedelta(days=1)

        duracion_jornada = (hora_salida - hora_entrada).seconds / 3600
        valor_hora = round(sueldo_mensual / (duracion_jornada * 5 * 4.33), 2)

        registros = []
        num_dias = calendar.monthrange(anio, mes)[1]

        # Recorrer los días del mes
        for dia in range(1, num_dias + 1):
            fecha = datetime(anio, mes, dia)
            fecha_str = fecha.strftime("%Y-%m-%d")
            dia_semana = fecha.weekday()  # 0=lunes, 6=domingo
            es_domingo_o_feriado = (dia_semana == 6) or (fecha_str in feriados)

            horas_extra = st.number_input(f"{fecha_str} - Horas extra:", min_value=0.0, step=1.0, key=dia)
            if horas_extra > 0:
                pago = calcular_pago_horas_extra(horas_extra, valor_hora, es_domingo_o_feriado)
                registros.append({
                    "Empleado": nombre_empleado,
                    "Fecha": fecha_str,
                    "Horas Extra": horas_extra,
                    "Pago Extra (S/)": pago
                })

        # Mostrar resultados
        if registros:
            df = pd.DataFrame(registros)
            st.subheader("📊 Reporte de Horas Extra del Mes")
            st.dataframe(df)
            st.write("💰 **Total de horas extra (S/):**", df["Pago Extra (S/)"].sum())

            # Exportar a Excel
            df.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
            st.success("Reporte guardado como 'HorasExtra_Mes_Reporte.xlsx'")
    else:
        st.warning("⚠️ Complete todos los campos para calcular.")

# Cerrar contenido
st.markdown("</div>", unsafe_allow_html=True)
