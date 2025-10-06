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
# ICONO, NOMBRE Y META PARA MÓVIL
# ==============================
st.markdown(
    """
    <meta name="apple-mobile-web-app-title" content="Horas Extra Marco">
    <link rel="apple-touch-icon" sizes="180x180" href="https://i.postimg.cc/ZnPMVtSs/RIVERPAZ.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    """,
    unsafe_allow_html=True
)

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
# ESTILOS: fondo dinámico y contenedor difuminado + texto con blur
# ==============================
st.markdown(
    """
    <style>
    /* Fondo dinámico */
    .stApp {
        background: linear-gradient(to bottom, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0) 40%),
                    url('https://i.postimg.cc/ZnPMVtSs/RIVERPAZ.png');
        background-size: cover;
        background-position: center;
        background-attachment: scroll;
    }

    /* Contenedor principal */
    .contenido {
        margin-top: 70vh;
        padding: 20px;
        border-radius: 10px;
        backdrop-filter: blur(8px);
        background-color: rgba(0,0,0,0.4);
        max-width: 90%;
        margin-left: auto;
        margin-right: auto;
    }

    /* Quitar padding extra de Streamlit */
    .block-container {
        padding-top: 0rem;
    }

    /* Texto con fondo difuminado */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stTextInput label, .stSelectbox label, .stButton button, .stAlert {
        background: rgba(0,0,0,0.45);
        backdrop-filter: blur(6px);
        border-radius: 8px;
        padding: 4px 8px;
        color: white !important;
        text-shadow: 0 0 10px rgba(0,0,0,0.8);
        display: inline-block;
    }

    /* Campos */
    input, .stTextInput>div>div>input {
        font-size: 1rem;
        background: rgba(255,255,255,0.3) !important;
        color: black !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
        backdrop-filter: blur(4px);
    }

    /* Botones */
    button {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: white !important;
        border-radius: 8px !important;
        transition: all 0.3s ease-in-out;
    }
    button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
    }

    /* DataFrame (tabla) */
    .stDataFrame {
        background: rgba(0,0,0,0.4) !important;
        backdrop-filter: blur(6px);
        border-radius: 8px;
        padding: 6px;
    }

    /* Ajuste de texto en móviles */
    input, label, p, button {
        font-size: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# CONTENIDO DE LA APP
# ==============================
with st.container():
    st.markdown('<div class="contenido"></div>', unsafe_allow_html=True)

# ----------------------
# BLOQUE DE DATOS GENERALES
# ----------------------
st.subheader("REGISTRO DE HORAS EXTRA")

nombre_empleado = st.text_input("Ingrese su nombre", value="")
sueldo_mensual = st.text_input("Ingrese su sueldo mensual (S/):", value="")
fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)")

# ----------------------
# BLOQUE HORAS EXTRA
# ----------------------
if fecha_seleccionada:
    fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")

    if st.session_state["ultima_fecha"] is not None and st.session_state["ultima_hora"] not in [None, ""]:
        try:
            st.session_state["registro_horas"][st.session_state["ultima_fecha"]] = float(st.session_state["ultima_hora"])
        except:
            st.session_state["registro_horas"][st.session_state["ultima_fecha"]] = 0

    valor_guardado = st.session_state["registro_horas"].get(fecha_str, "")
    horas_extra_val = st.text_input(
        f"Horas extra del día {fecha_str}:",
        value=str(valor_guardado) if valor_guardado != "" else ""
    )

    st.session_state["ultima_fecha"] = fecha_str
    st.session_state["ultima_hora"] = horas_extra_val

# ----------------------
# BOTONES CALCULAR Y LIMPIAR
# ----------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("Calcular Horas Extra"):
        if nombre_empleado.strip() != "" and sueldo_mensual.strip() != "":
            try:
                sueldo_mensual_val = float(sueldo_mensual)
            except:
                st.warning("⚠️ El sueldo debe ser un número válido.")
                st.stop()

            if st.session_state["ultima_fecha"] is not None and st.session_state["ultima_hora"] not in [None, ""]:
                try:
                    st.session_state["registro_horas"][st.session_state["ultima_fecha"]] = float(st.session_state["ultima_hora"])
                except:
                    st.session_state["registro_horas"][st.session_state["ultima_fecha"]] = 0

            valor_hora = round(sueldo_mensual_val / (8 * 5 * 4.33), 2)
            registros = []

            anio = fecha_seleccionada.year
            peru_feriados = holidays.Peru(years=anio)
            feriados = [f.strftime("%Y-%m-%d") for f in peru_feriados.keys()]

            for f_str, h in st.session_state["registro_horas"].items():
                if h not in ["", None]:
                    h = float(h)
                    fecha = datetime.strptime(f_str, "%Y-%m-%d")
                    dia_semana = fecha.weekday()
                    es_domingo_o_feriado = dia_semana == 6 or f_str in feriados

                    if es_domingo_o_feriado:
                        pago = round(h * valor_hora * 2, 2)
                    else:
                        if h <= 2:
                            pago = round(h * valor_hora * 1.25, 2)
                        else:
                            pago = round(2 * valor_hora * 1.25 + (h - 2) * valor_hora * 1.35, 2)

                    registros.append({
                        "Empleado": nombre_empleado,
                        "Fecha": f_str,
                        "Horas Extra": h,
                        "Pago Extra (S/)": pago
                    })

            if registros:
                df = pd.DataFrame(registros)
                st.subheader("📊 Reporte de Horas Extra")
                st.dataframe(df)
                st.write("💰 **Total de horas extra (S/):**", df["Pago Extra (S/)"].sum())

                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)

                st.download_button(
                    label="📥 Descargar Excel",
                    data=output,
                    file_name="HorasExtra_Mes_Reporte.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No se ingresaron horas extra.")
        else:
            st.warning("⚠️ Complete todos los campos.")

with col2:
    if st.button("Limpiar Hrs Ext."):
        st.session_state["registro_horas"].clear()
        st.session_state["ultima_fecha"] = None
        st.session_state["ultima_hora"] = None
        st.success("✅ Historial de horas extra borrado correctamente")
