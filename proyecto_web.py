import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
from io import BytesIO

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
    st.session_state["registro_horas"] = {}

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
# ESTILOS (Fondos, botones, paralaje)
# ==============================
st.markdown(
    """
    <style>
    /* ===== FONDO PRINCIPAL ===== */
    .stApp {
        background: url('https://i.postimg.cc/ZnPMVtSs/RIVERPAZ.png') no-repeat center center fixed;
        background-size: cover;
        position: relative;
        z-index: 0;
    }

    /* ===== EFECTO DE CAPA FIJA (PARTE SUPERIOR) ===== */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 40vh; /* Parte fija visible */
        background: inherit;
        background-attachment: fixed;
        z-index: -1;
    }

    /* ===== FONDO PARA MÓVIL ===== */
    @media (max-width: 768px) {
        .stApp {
            background: url('https://i.postimg.cc/7h9C7YK2/IMG-APP.png') no-repeat center center;
            background-size: cover;
            background-attachment: scroll;
        }

        .stApp::before {
            background: url('https://i.postimg.cc/7h9C7YK2/IMG-APP.png') no-repeat center top;
            background-size: cover;
            background-attachment: fixed;
            height: 35vh;
        }
    }

    /* ===== CONTENIDO ===== */
    .contenido {
        margin-top: 45vh;
        padding: 25px;
        border-radius: 10px;
        backdrop-filter: blur(8px);
        background-color: rgba(0,0,0,0.45);
        max-width: 90%;
        margin-left: auto;
        margin-right: auto;
    }

    .block-container {
        padding-top: 0rem !important;
    }

    /* ===== TEXTO ===== */
    body, .stApp, .stMarkdown, .stText, label, h1, h2, h3, p, span, div {
        color: white !important;
    }

    /* ===== INPUTS OSCUROS ===== */
    input, textarea, select, .stTextInput>div>div>input, 
    .stNumberInput>div>div>input, .stDateInput input {
        background-color: rgba(30,30,30,0.85) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #555 !important;
    }

    ::placeholder {
        color: #cccccc !important;
    }

    /* ===== BOTONES OSCUROS ===== */
    div.stButton > button {
        background-color: rgba(0, 0, 0, 0.75) !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.2s ease-in-out !important;
    }

    div.stButton > button:hover {
        background-color: rgba(30, 30, 30, 0.9) !important;
        border: 1px solid #888 !important;
        transform: scale(1.03);
    }

    @media (max-width: 768px) {
        div.stButton > button {
            width: 100% !important;
            font-size: 1.1rem !important;
            padding: 0.8rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# CONTENIDO DE LA APP
# ==============================
with st.container():
    st.markdown('<div class="contenido">', unsafe_allow_html=True)
    st.subheader("REGISTRO DE HORAS EXTRA")

    # ----------------------
    # ENTRADAS
    # ----------------------
    nombre_empleado = st.text_input("Ingrese su nombre", value="")
    sueldo_mensual = st.text_input("Ingrese su sueldo mensual (S/):", value="")
    fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)")

    # ----------------------
    # REGISTRO DE HORAS
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
    # BOTONES
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

    st.markdown('</div>', unsafe_allow_html=True)
