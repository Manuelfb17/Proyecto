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
# Estilos personalizados (modo oscuro solo para letras e inputs)
# ==============================
st.markdown("""
<style>
/* Mantiene tu margen original */
.main {
    margin-top: 70vh;
}

/* Aplica modo oscuro solo al texto */
body, .stApp {
    color: #f0f0f0 !important;  /* Letras claras */
}

/* Cuadros donde escribes información */
input, select, textarea, .stTextInput, .stTextArea, .stSelectbox, .stNumberInput {
    background-color: #1e1e1e !important;  /* Fondo oscuro */
    color: #ffffff !important;  /* Texto blanco */
    border: 1px solid #444 !important;  /* Borde gris suave */
    border-radius: 8px !important;
}

/* Evita que el color afecte al fondo principal */
.stApp {
    background: transparent !important;
}

/* Etiquetas, títulos y textos */
label, .stMarkdown, .stText, .stSelectbox label {
    color: #f5f5f5 !important;
}
</style>
""", unsafe_allow_html=True)


# ==============================
# Título de la aplicación
# ==============================
st.title("Registro de Horas Extra 🕒")

# ==============================
# Formulario principal
# ==============================
with st.form("registro_form"):
    fecha = st.date_input("Fecha")
    hora_inicio = st.time_input("Hora de inicio")
    hora_fin = st.time_input("Hora de fin")
    descripcion = st.text_area("Descripción de la tarea realizada")
    enviado = st.form_submit_button("Registrar")

# ==============================
# Procesamiento
# ==============================
if enviado:
    st.session_state["registro_horas"][fecha] = {
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "descripcion": descripcion
    }
    st.success("✅ Registro guardado correctamente.")

# ==============================
# Mostrar historial
# ==============================
st.subheader("Historial de registros")
if st.session_state["registro_horas"]:
    df = pd.DataFrame.from_dict(st.session_state["registro_horas"], orient="index")
    st.dataframe(df)
else:
    st.info("No hay registros aún.")
