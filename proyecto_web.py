import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import gspread
from google.oauth2.service_account import Credentials

# ==============================
# CONFIGURACIÓN DE GOOGLE SHEETS
# ==============================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "horasextramarco-f6c3648f7519.json"
SPREADSHEET_NAME = "Registro_Horas_Extra"  # Nombre de tu hoja en Google Sheets

# Autenticación
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
client = gspread.authorize(creds)

# Abrir hoja de cálculo, crear si no existe
try:
    sheet = client.open(SPREADSHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    sheet = client.create(SPREADSHEET_NAME).sheet1
    sheet.append_row(["Fecha", "Empleado", "Horas Extra"])

# ==============================
# CONFIGURACIÓN DE STREAMLIT
# ==============================
st.set_page_config(
    page_title="Registro de Horas Extra",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# ESTILOS
# ==============================
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
}
.campo-datos {
    margin-bottom: 20px;
}
.block-container {
    padding-top: 0rem;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# FUNCIONES PARA GOOGLE SHEETS
# ==============================
def obtener_datos():
    """Obtiene todos los datos guardados en Google Sheets como DataFrame"""
    datos = sheet.get_all_records()
    df = pd.DataFrame(datos)
    return df

def guardar_hora(fecha, empleado, horas):
    """Guarda o actualiza una hora extra para una fecha y empleado"""
    datos = sheet.get_all_records()
    # Verificar si ya hay registro para esa fecha y empleado
    fila_existente = None
    for i, fila in enumerate(datos):
        if fila["Fecha"] == fecha and fila["Empleado"] == empleado:
            fila_existente = i + 2  # +2 por encabezados y 1-index en Sheets
            break
    if fila_existente:
        sheet.update_cell(fila_existente, 3, horas)
    else:
        sheet.append_row([fecha, empleado, horas])

def limpiar_todo():
    """Limpia todos los datos de Google Sheets"""
    sheet.clear()
    sheet.append_row(["Fecha", "Empleado", "Horas Extra"])

# ==============================
# INTERFAZ DE LA APP
# ==============================
st.subheader("REGISTRO DE HORAS EXTRA")

# Campos vacíos por defecto
nombre_empleado = st.text_input("Ingrese su nombre", value="")
sueldo_mensual = st.number_input(
    "Ingrese su sueldo mensual (S/):",
    min_value=0,
    step=100,
    format="%d",
    value=None
)
fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)")

# Bloque de horas extra
horas_extra = None
if fecha_seleccionada and nombre_empleado:
    fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")
    df_guardado = obtener_datos()
    # Si ya hay horas para esta fecha y empleado, mostrar
    registro = df_guardado[(df_guardado["Fecha"] == fecha_str) & (df_guardado["Empleado"] == nombre_empleado)]
    if not registro.empty:
        horas_extra = st.number_input(
            f"Horas extra del día seleccionado:",
            min_value=0,
            step=1,
            value=int(registro.iloc[0]["Horas Extra"])
        )
    else:
        horas_extra = st.number_input(
            f"Horas extra del día seleccionado:",
            min_value=0,
            step=1,
            value=0
        )

# Guardar horas en Google Sheets al cambiar
if horas_extra is not None and fecha_seleccionada and nombre_empleado:
    guardar_hora(fecha_str, nombre_empleado, horas_extra)

# Botón para limpiar todo
if st.button("Limpiar Hrs. Ext."):
    limpiar_todo()
    st.experimental_rerun()

# ----------------------
# BOTÓN CALCULAR Y TABLA
# ----------------------
if st.button("Calcular Horas Extra"):
    if nombre_empleado and sueldo_mensual:
        valor_hora = round(sueldo_mensual / (8 * 5 * 4.33), 2)
        registros = []
        df_guardado = obtener_datos()
        peru_feriados = holidays.Peru(years=datetime.now().year)
        feriados = [fecha.strftime("%Y-%m-%d") for fecha in peru_feriados.keys()]

        for _, fila in df_guardado.iterrows():
            fecha_str = fila["Fecha"]
            horas = fila["Horas Extra"]
            fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
            dia_semana = fecha_dt.weekday()
            es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (fecha_str in feriados)

            if es_domingo_o_feriado:
                pago = round(horas * valor_hora * 2, 2)
            else:
                if horas <= 2:
                    pago = round(horas * valor_hora * 0.25, 2)
                else:
                    pago = round(2*valor_hora*0.25 + (horas-2)*valor_hora*0.35, 2)

            registros.append({
                "Empleado": fila["Empleado"],
                "Fecha": fecha_str,
                "Horas Extra": horas,
                "Pago Extra (S/)": pago
            })

        if registros:
            df_reporte = pd.DataFrame(registros)
            st.subheader("📊 Reporte de Horas Extra")
            st.dataframe(df_reporte)
            st.write("💰 **Total de horas extra (S/):**", df_reporte["Pago Extra (S/)"].sum())
            # Botón para descargar Excel
            df_reporte.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
            st.download_button("📥 Descargar Excel", df_reporte.to_excel(index=False, engine='xlsxwriter'), file_name="HorasExtra_Mes_Reporte.xlsx")
        else:
            st.info("No se ingresaron horas extra.")
    else:
        st.warning("⚠️ Complete todos los campos.")
