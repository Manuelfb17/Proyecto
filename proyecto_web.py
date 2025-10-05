import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# ==========================
# CONFIGURACIÓN DE LA APP
# ==========================
st.set_page_config(page_title="Cálculo de Horas y Asistencia", layout="wide")

st.title("📅 Cálculo de Jornada y Horas Extras - Marco Peruana")

# ==========================
# DATOS BASE
# ==========================
SUELDO_MENSUAL = 1500
HORAS_DIARIAS = 9  # 8 a.m. - 6 p.m. (con 1 hora de almuerzo)
DIAS_LABORALES = 5  # Lunes a viernes

# ==========================
# CÁLCULOS
# ==========================
sueldo_diario = SUELDO_MENSUAL / 30
sueldo_hora = sueldo_diario / HORAS_DIARIAS

st.write(f"💰 **Sueldo mensual:** S/ {SUELDO_MENSUAL:.2f}")
st.write(f"🕒 **Sueldo diario:** S/ {sueldo_diario:.2f}")
st.write(f"💵 **Sueldo por hora normal:** S/ {sueldo_hora:.2f}")

# ==========================
# HORAS EXTRA
# ==========================
st.subheader("💼 Cálculo de horas extra")

horas_extra = st.number_input("Ingrese las horas extra realizadas:", min_value=0, step=1, value=0)

if horas_extra > 0:
    if horas_extra <= 2:
        pago_extra = horas_extra * (sueldo_hora * 1.25)
    else:
        pago_extra = (2 * sueldo_hora * 1.25) + ((horas_extra - 2) * sueldo_hora * 1.35)

    st.success(f"✅ Pago total por {horas_extra} hora(s) extra: S/ {pago_extra:.2f}")
else:
    st.info("No se registraron horas extra.")

# ==========================
# CALENDARIO DE ASISTENCIA (EN ESPAÑOL)
# ==========================
st.subheader("📆 Calendario de Asistencias")

calendar_config = {
    "initialView": "dayGridMonth",
    "buttonText": {
        "today": "Hoy",
        "month": "Mes",
        "week": "Semana",
        "day": "Día"
    },
    "dayHeaderFormat": {"weekday": "short"},  # Lu, Ma, Mi, Ju, Vi...
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    }
}

# Ejemplo de eventos en el calendario
eventos = [
    {"title": "Turno completo", "start": "2025-10-01", "color": "#16a34a"},
    {"title": "4h extra", "start": "2025-10-02", "color": "#2563eb"},
    {"title": "Feriado", "start": "2025-10-03", "color": "#dc2626"},
]

cal_event = calendar(events=eventos, options=calendar_config, key="calendario_es")

# ==========================
# TOTAL DIARIO CON HORAS EXTRA
# ==========================
if horas_extra > 0:
    total_dia = sueldo_diario + pago_extra
else:
    total_dia = sueldo_diario

st.markdown("---")
st.write(f"📊 **Total ganado en el día (incluyendo horas extra): S/ {total_dia:.2f}**")
