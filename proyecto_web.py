import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import gspread
from google.oauth2.service_account import Credentials

# ==============================
# Configuración Google Sheets
# ==============================
SERVICE_ACCOUNT_FILE = "horasextramarco-f6c3648f7519.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

client = gspread.authorize(creds)

# Reemplaza con tu Sheet ID
SHEET_ID = "TU_ID_DE_HOJA_DE_CALCULO"
SHEET_NAME = "HorasExtra"

try:
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
except:
    # Si la hoja no existe, crea una
    sheet = client.open_by_key(SHEET_ID).add_worksheet(title=SHEET_NAME, rows="100", cols="10")
    sheet.append_row(["Empleado", "Fecha", "Horas Extra", "Pago Extra (S/)"])

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
    st.session_state["registro_horas"] = {}  # Diccionario temporal para la sesión

# ==============================
# Streamlit Página y Estilos
# ==============================
st.set_page_config(
    page_title="Registro de Horas Extra",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        margin-top: 20px;
        padding: 20px;
        border-radius: 10px;
        background-color: rgba(255,255,255,0.2);
        backdrop-filter: blur(8px);
    }
    .campo-datos { margin-bottom: 20px; }
    .block-container { padding-top: 0rem; }
    </style>
""", unsafe_allow_html=True)

# ==============================
# Contenido de la App
# ==============================
with st.container():
    st.markdown('<div class="contenido"></div>', unsafe_allow_html=True)
    st.subheader("REGISTRO DE HORAS EXTRA")

    # ----------------------
    # Campos vacíos por defecto
    # ----------------------
    nombre_empleado = st.text_input("Ingrese su nombre", value="")
    sueldo_mensual = st.number_input(
        "Ingrese su sueldo mensual (S/):",
        min_value=0,
        step=100,
        format="%d",
        value=None
    )
    fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)")

    fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")

    # Cargar horas ya guardadas para esa fecha
    try:
        data = sheet.get_all_records()
        df_sheet = pd.DataFrame(data)
        horas_previas = df_sheet.loc[(df_sheet["Fecha"]==fecha_str) & (df_sheet["Empleado"]==nombre_empleado), "Horas Extra"]
        horas_valor = int(horas_previas.iloc[0]) if not horas_previas.empty else None
    except:
        horas_valor = None

    horas_extra = st.number_input(
        f"Horas extra del día seleccionado:",
        min_value=0,
        step=1,
        value=horas_valor
    )

    st.session_state["registro_horas"][fecha_str] = horas_extra

    # ==============================
    # BOTONES
    # ==============================
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Calcular Horas Extra"):
            if nombre_empleado and sueldo_mensual:
                valor_hora = round(sueldo_mensual / (8*5*4.33), 2)
                registros = []

                for fecha, horas in st.session_state["registro_horas"].items():
                    if horas:
                        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
                        dia_semana = fecha_dt.weekday()
                        peru_feriados = holidays.Peru(years=fecha_dt.year)
                        feriados = [f.strftime("%Y-%m-%d") for f in peru_feriados.keys()]
                        es_domingo_o_feriado = (dia_semana==5 or dia_semana==6) or (fecha in feriados)

                        if es_domingo_o_feriado:
                            pago = round(horas * valor_hora * 2, 2)
                        else:
                            if horas<=2:
                                pago = round(horas*valor_hora*0.25,2)
                            else:
                                pago = round(2*valor_hora*0.25 + (horas-2)*valor_hora*0.35,2)

                        registros.append({
                            "Empleado": nombre_empleado,
                            "Fecha": fecha,
                            "Horas Extra": horas,
                            "Pago Extra (S/)": pago
                        })

                        # Guardar en Google Sheets
                        try:
                            df_exist = pd.DataFrame(sheet.get_all_records())
                            fila_existente = df_exist.loc[(df_exist["Fecha"]==fecha) & (df_exist["Empleado"]==nombre_empleado)].index
                            if not fila_existente.empty:
                                sheet.update_cell(fila_existente[0]+2, 3, horas)
                                sheet.update_cell(fila_existente[0]+2, 4, pago)
                            else:
                                sheet.append_row([nombre_empleado, fecha, horas, pago])
                        except:
                            sheet.append_row([nombre_empleado, fecha, horas, pago])

                if registros:
                    df = pd.DataFrame(registros)
                    st.subheader("📊 Reporte de Horas Extra")
                    st.dataframe(df)
                    st.write("💰 **Total de horas extra (S/):**", df["Pago Extra (S/)"].sum())
            else:
                st.warning("⚠️ Complete todos los campos.")

    with col2:
        if st.button("Limpiar Horas Extra"):
            st.session_state["registro_horas"] = {}
            st.experimental_rerun()

    with col3:
        if st.button("Descargar Excel"):
            df_download = pd.DataFrame(sheet.get_all_records())
            df_download.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
            st.success("Reporte guardado como 'HorasExtra_Mes_Reporte.xlsx'")
