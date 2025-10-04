import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import gspread
from google.oauth2.service_account import Credentials

# ==============================
# CONFIGURACIÓN GOOGLE SHEETS
# ==============================
# Ruta a tu JSON descargado
SERVICE_ACCOUNT_FILE = "credenciales.json"

# Permisos que necesitamos
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# Abre la hoja de cálculo por nombre
SHEET_NAME = "HorasExtraMarco"  # pon el nombre de tu sheet
sheet = client.open(SHEET_NAME).sheet1  # puedes usar sheet1 o seleccionar otra hoja

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

# ==============================
# ESTILOS
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

    st.subheader("REGISTRO DE HORAS EXTRA")
    nombre_empleado = st.text_input("Ingrese su nombre", value="")
    sueldo_mensual = st.number_input("Ingrese su sueldo mensual (S/):", min_value=0, step=100, format="%d", value=None)
    fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)")

    if fecha_seleccionada:
        anio = fecha_seleccionada.year
        fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")

        # Cargar datos desde Google Sheets
        all_data = sheet.get_all_records()
        df_sheet = pd.DataFrame(all_data)
        # Filtra si ya hay registro para la fecha seleccionada
        horas_extra_default = None
        if not df_sheet.empty:
            filtro = df_sheet[(df_sheet['Fecha'] == fecha_str) & (df_sheet['Empleado'] == nombre_empleado)]
            if not filtro.empty:
                horas_extra_default = filtro.iloc[0]["Horas Extra"]

        peru_feriados = holidays.Peru(years=anio)
        feriados = [f.strftime("%Y-%m-%d") for f in peru_feriados.keys()]

        st.subheader(f"Ingrese las horas extra para {fecha_str}")
        horas_extra = st.number_input(
            f"Horas extra del día seleccionado:",
            min_value=0,
            step=1,
            format="%d",
            value=horas_extra_default
        )

        st.session_state["registro_horas"][fecha_str] = horas_extra

    # ----------------------
    # BOTÓN CALCULAR
    # ----------------------
    if st.button("Calcular Horas Extra"):
        if nombre_empleado and sueldo_mensual:
            valor_hora = round(sueldo_mensual / (8 * 5 * 4.33), 2)
            registros = []

            for fecha_str, horas in st.session_state["registro_horas"].items():
                if horas:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    dia_semana = fecha.weekday()
                    es_domingo_o_feriado = (dia_semana >= 5) or (fecha_str in feriados)
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

            # Guardar en Google Sheets
            for r in registros:
                sheet.append_row([r["Empleado"], r["Fecha"], r["Horas Extra"], r["Pago Extra (S/)"]])

            df = pd.DataFrame(registros)
            st.subheader("📊 Reporte de Horas Extra")
            st.dataframe(df)
            st.success("Datos guardados en Google Sheets ✅")

