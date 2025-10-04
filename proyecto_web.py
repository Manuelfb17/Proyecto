import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import json
import os

# ==============================
# CONFIGURACIÓN PÁGINA
# ==============================
st.set_page_config(
    page_title="Registro de Horas Extra",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# ICONO Y NOMBRE PARA IOS (PWA)
# ==============================
st.markdown("""
<meta name="apple-mobile-web-app-title" content="Horas Extra Marco">
<link rel="apple-touch-icon" sizes="180x180" href="https://i.postimg.cc/7PjfgKkz/marco-peruana.png">
<meta name="apple-mobile-web-app-capable" content="yes">
""", unsafe_allow_html=True)

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
# CARGAR HISTORIAL DESDE JSON
# ==============================
historial = {}
if os.path.exists("registro_horas.json"):
    with open("registro_horas.json", "r") as f:
        historial = json.load(f)

if "registro_horas" not in st.session_state:
    st.session_state["registro_horas"] = historial

# ==============================
# CONTENEDOR PRINCIPAL
# ==============================
with st.container():
    st.markdown('<div class="contenido"></div>', unsafe_allow_html=True)
    st.subheader("REGISTRO DE HORAS EXTRA")
    
    # Campos vacíos por defecto
    nombre_empleado = st.text_input("Ingrese su nombre")
    sueldo_mensual = st.text_input("Ingrese su sueldo mensual (S/)")
    
    # Fecha inicialmente vacía (streamlit no permite vaciar date_input, se usa workaround)
    fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)", key="fecha", value=None)

# ==============================
# HORAS EXTRA POR FECHA
# ==============================
horas_extra = None
if fecha_seleccionada:
    anio = fecha_seleccionada.year
    fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")

    peru_feriados = holidays.Peru(years=anio)
    feriados = [fecha.strftime("%Y-%m-%d") for fecha in peru_feriados.keys()]

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader(f"Ingrese las horas extra para {fecha_str}")

    # Campo vacío cada vez que cambia la fecha
    horas_extra = st.number_input(
        "Horas extra del día seleccionado:",
        min_value=0,
        step=1,
        format="%d",
        value=None
    )

# ==============================
# BOTONES
# ==============================
col1, col2 = st.columns(2)

with col1:
    if st.button("Calcular Horas Extra"):
        if nombre_empleado and sueldo_mensual:
            # Convertir sueldo a float
            try:
                sueldo = float(sueldo_mensual)
            except:
                st.warning("Ingrese un sueldo válido")
                st.stop()

            # Guardar solo si se ingresó horas
            if fecha_seleccionada and horas_extra is not None:
                historial[fecha_str] = horas_extra

            valor_hora = round(sueldo / (8 * 5 * 4.33), 2)
            registros = []

            for fecha, horas in historial.items():
                if horas:
                    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
                    dia_semana = fecha_dt.weekday()
                    es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (fecha in feriados)

                    if es_domingo_o_feriado:
                        pago = round(horas * valor_hora * 2, 2)
                    else:
                        if horas <= 2:
                            pago = round(horas * valor_hora * 0.25, 2)
                        else:
                            pago = round(2*valor_hora*0.25 + (horas-2)*valor_hora*0.35, 2)

                    registros.append({
                        "Empleado": nombre_empleado,
                        "Fecha": fecha,
                        "Horas Extra": horas,
                        "Pago Extra (S/)": pago
                    })

            # Guardar historial actualizado
            with open("registro_horas.json", "w") as f:
                json.dump(historial, f)

            if registros:
                df = pd.DataFrame(registros)
                st.subheader("📊 Reporte de Horas Extra")
                st.dataframe(df)
                st.write("💰 **Total de horas extra (S/):**", df["Pago Extra (S/)"].sum())
                df.to_excel("HorasExtra_Mes_Reporte.xlsx", index=False)
                st.success("Reporte guardado como 'HorasExtra_Mes_Reporte.xlsx'")
            else:
                st.info("No se ingresaron horas extra.")
        else:
            st.warning("⚠️ Complete todos los campos.")

with col2:
    if st.button("🧹 Limpiar Hrs Ext."):
        if os.path.exists("registro_horas.json"):
            os.remove("registro_horas.json")
        st.session_state["registro_horas"].clear()
        historial.clear()
        st.success("✅ Historial de horas extra limpiado.")

# ==============================
# MOSTRAR REPORTE AUTOMÁTICO SI HAY HISTORIAL
# ==============================
if historial:
    if nombre_empleado and sueldo_mensual:
        try:
            sueldo = float(sueldo_mensual)
        except:
            sueldo = 0
        valor_hora = round(sueldo / (8 * 5 * 4.33), 2)
    registros = []
    for fecha, horas in historial.items():
        if horas:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            dia_semana = fecha_dt.weekday()
            es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (fecha in feriados)
            if es_domingo_o_feriado:
                pago = round(horas * valor_hora * 2, 2)
            else:
                if horas <= 2:
                    pago = round(horas * valor_hora * 0.25, 2)
                else:
                    pago = round(2*valor_hora*0.25 + (horas-2)*valor_hora*0.35, 2)
            registros.append({
                "Empleado": nombre_empleado,
                "Fecha": fecha,
                "Horas Extra": horas,
                "Pago Extra (S/)": pago
            })
    df = pd.DataFrame(registros)
    st.subheader("📊 Historial de Horas Extra")
    st.dataframe(df)
    st.write("💰 **Total de horas extra (S/):**", df["Pago Extra (S/)"].sum())
