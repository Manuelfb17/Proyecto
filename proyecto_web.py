import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
from io import BytesIO

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
    st.session_state["registro_horas"] = {}  # Guarda todas las horas ingresadas

if "ultima_fecha" not in st.session_state:
    st.session_state["ultima_fecha"] = None

if "ultima_hora" not in st.session_state:
    st.session_state["ultima_hora"] = None

# ==============================
# Fondo con imagen + texto con fondo difuminado
# ==============================
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://i.imgur.com/W8yHxxr.jpeg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Color y sombra general de texto */
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stTextInput label {
    color: white !important;
    text-shadow: 0 0 8px rgba(0,0,0,0.8);
}

/* Cajas difuminadas detrás del texto */
.block-container, .stMarkdown, .stDataFrame, .stTextInput, .stSelectbox, .stButton, .stAlert {
    background: rgba(0,0,0,0.4);
    backdrop-filter: blur(6px);
    border-radius: 12px;
    padding: 10px;
}

/* Botones */
button {
    color: white !important;
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 10px !important;
    transition: all 0.3s ease-in-out;
}
button:hover {
    background: rgba(255, 255, 255, 0.3) !important;
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ==============================
# Título
# ==============================
st.title("🕒 Registro de horas laborales")

# ==============================
# Feriados Perú
# ==============================
feriados_pe = holidays.Peru()

def es_feriado(fecha):
    return fecha in feriados_pe

# ==============================
# Registro
# ==============================
nombre = st.text_input("Ingrese su nombre:")
accion = st.selectbox("Seleccione acción:", ["Entrada", "Salida"])
fecha_actual = datetime.now().strftime("%Y-%m-%d")
hora_actual = datetime.now().strftime("%H:%M:%S")

if st.button("Registrar"):
    if nombre:
        if fecha_actual not in st.session_state["registro_horas"]:
            st.session_state["registro_horas"][fecha_actual] = []
        st.session_state["registro_horas"][fecha_actual].append({
            "Nombre": nombre,
            "Acción": accion,
            "Hora": hora_actual
        })
        st.session_state["ultima_fecha"] = fecha_actual
        st.session_state["ultima_hora"] = hora_actual
        st.success(f"{accion} registrada correctamente a las {hora_actual}")
    else:
        st.warning("Por favor, ingrese su nombre antes de registrar.")

# ==============================
# Mostrar registros del día
# ==============================
st.subheader("📋 Registros del día")
if fecha_actual in st.session_state["registro_horas"]:
    df = pd.DataFrame(st.session_state["registro_horas"][fecha_actual])
    st.dataframe(df)
else:
    st.info("Aún no hay registros para hoy.")

# ==============================
# Exportar a Excel
# ==============================
def exportar_excel():
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    for fecha, registros in st.session_state["registro_horas"].items():
        df = pd.DataFrame(registros)
        df.to_excel(writer, index=False, sheet_name=fecha[:10])
    writer.close()
    return output.getvalue()

if st.button("📤 Exportar a Excel"):
    excel_data = exportar_excel()
    st.download_button(
        label="Descargar archivo Excel",
        data=excel_data,
        file_name="registro_horas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
