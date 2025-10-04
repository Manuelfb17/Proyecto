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
# ESTILOS: fondo dinámico difuminado
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
""", unsafe_allow_html=True)

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

        # Guardar valor anterior antes de limpiar el campo
        if st.session_state["ultima_fecha"] and st.session_state["ultima_hora"] not in [None, ""]:
            st.session_state["registro_horas"][st.session_state["ultima_fecha"]] = float(st.session_state["ultima_hora"])

        # Campo vacío para la nueva fecha
        horas_extra_val = st.text_input(f"Horas extra del día {fecha_str}:", value="")

        # Guardar temporalmente
        st.session_state["ultima_fecha"] = fecha_str
        st.session_state["ultima_hora"] = horas_extra_val

    # ----------------------
    # BOTONES
    # ----------------------
    col1, col2 = st.columns(2)
    with col1:
        calcular = st.button("Calcular Horas Extra")
    with col2:
        limpiar = st.button("Limpiar Hrs Ext.")

    # ----------------------
    # ACCIÓN LIMPIAR
    # ----------------------
    if limpiar:
        st.session_state["registro_horas"] = {}
        st.session_state["ultima_fecha"] = None
        st.session_state["ultima_hora"] = None
        st.experimental_rerun()

    # ----------------------
    # ACCIÓN CALCULAR
    # ----------------------
    if calcular:
        # Guardar la última fecha activa
        if st.session_state["ultima_fecha"] and st.session_state["ultima_hora"] not in [None, ""]:
            st.session_state["registro_horas"][st.session_state["ultima_fecha"]] = float(st.session_state["ultima_hora"])

        if nombre_empleado and sueldo_mensual:
            try:
                sueldo_mensual_val = float(sueldo_mensual)
            except:
                st.warning("Ingrese un sueldo válido.")
                st.stop()

            valor_hora = round(sueldo_mensual_val / (8 * 5 * 4.33), 2)
            registros = []

            # Calcular feriados
            anio_actual = datetime.now().year
            peru_feriados = holidays.Peru(years=anio_actual)
            feriados = [fecha.strftime("%Y-%m-%d") for fecha in peru_feriados.keys()]

            for fecha_str, horas in st.session_state["registro_horas"].items():
                if horas:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    dia_semana = fecha.weekday()  # 0=lunes, 6=domingo
                    es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (fecha_str in feriados)

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

            if registros:
                df = pd.DataFrame(registros)
                st.subheader("📊 Reporte de Horas Extra")
                st.dataframe(df)
                st.write("💰 **Total de horas extra (S/):**", df["Pago Extra (S/)"].sum())

                # Botón para descargar Excel
                towrite = BytesIO()
                df.to_excel(towrite, index=False, engine='openpyxl')
                towrite.seek(0)
                st.download_button(
                    label="📥 Descargar Excel",
                    data=towrite,
                    file_name="HorasExtra_Mes_Reporte.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No se ingresaron horas extra.")
        else:
            st.warning("⚠️ Complete todos los campos.")
