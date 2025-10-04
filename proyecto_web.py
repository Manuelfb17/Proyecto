import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
from io import BytesIO
import os

# Archivo para guardar datos
archivo_datos = "registro_horas.csv"

# ==============================
# Configuración inicial de sesión
# ==============================
if "registro_horas" not in st.session_state:
    if os.path.exists(archivo_datos):
        df_guardado = pd.read_csv(archivo_datos)
        registro_horas = {row["Fecha"]: row["Horas Extra"] for _, row in df_guardado.iterrows()}
        st.session_state["registro_horas"] = registro_horas
    else:
        st.session_state["registro_horas"] = {}

# ==============================
# Configuración PWA e icono
# ==============================
st.markdown("""
<meta name="apple-mobile-web-app-title" content="Horas Extra Marco">
<link rel="apple-touch-icon" sizes="180x180" href="https://i.postimg.cc/7PjfgKkz/marco-peruana.png">
<meta name="apple-mobile-web-app-capable" content="yes">
""", unsafe_allow_html=True)

# Configuración de la página
st.set_page_config(
    page_title="Registro de Horas Extra",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos
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
</style>
""", unsafe_allow_html=True)

# Contenedor principal
with st.container():
    st.markdown('<div class="contenido"></div>', unsafe_allow_html=True)
    st.subheader("REGISTRO DE HORAS EXTRA")

    # Campos vacíos sin valores por defecto
    nombre_empleado = st.text_input("Ingrese su nombre", value="")
    sueldo_mensual = st.text_input("Ingrese su sueldo mensual (S/):", value="")  # ahora es text_input vacío
    fecha_seleccionada = st.date_input("Seleccione la fecha (día, mes y año)")

    # Contenedor para horas extra vacío
    horas_extra_input = st.empty()
    horas_extra_val = None
    if fecha_seleccionada:
        fecha_str = fecha_seleccionada.strftime("%Y-%m-%d")
        horas_extra_val = horas_extra_input.text_input(
            f"Horas extra del día {fecha_str}:", value=""
        )

    # Botón Limpiar historial
    if st.button("Limpiar HRS EXT."):
        st.session_state["registro_horas"] = {}
        if os.path.exists(archivo_datos):
            os.remove(archivo_datos)
        st.success("Historial de horas extra limpiado!")

    # Botón Calcular
    if st.button("Calcular Horas Extra"):
        if nombre_empleado.strip() and sueldo_mensual.strip() and fecha_seleccionada:
            try:
                sueldo_val = float(sueldo_mensual)
            except ValueError:
                st.warning("Ingrese un sueldo válido")
                st.stop()

            if horas_extra_val.strip() != "":
                horas_val = float(horas_extra_val)
            else:
                horas_val = 0

            st.session_state["registro_horas"][fecha_str] = horas_val

            # Guardar CSV
            df_guardar = pd.DataFrame([
                {"Empleado": nombre_empleado,
                 "Fecha": f,
                 "Horas Extra": h,
                 "Pago Extra (S/)": 0}
                for f, h in st.session_state["registro_horas"].items()
            ])
            df_guardar.to_csv(archivo_datos, index=False)

            # Calcular pagos
            registros = []
            anio = fecha_seleccionada.year
            peru_feriados = holidays.Peru(years=anio)
            feriados = [fecha.strftime("%Y-%m-%d") for fecha in peru_feriados.keys()]

            for f, h in st.session_state["registro_horas"].items():
                fecha_obj = datetime.strptime(f, "%Y-%m-%d")
                dia_semana = fecha_obj.weekday()
                es_domingo_o_feriado = (dia_semana == 5 or dia_semana == 6) or (f in feriados)

                valor_hora = round(sueldo_val / (8*5*4.33), 2)
                if es_domingo_o_feriado:
                    pago = round(h * valor_hora * 2, 2)
                else:
                    if h <= 2:
                        pago = round(h * valor_hora * 0.25, 2)
                    else:
                        pago = round(2*valor_hora*0.25 + (h-2)*valor_hora*0.35, 2)

                registros.append({
                    "Empleado": nombre_empleado,
                    "Fecha": f,
                    "Horas Extra": h,
                    "Pago Extra (S/)": pago
                })

            if registros:
                df = pd.DataFrame(registros)
                st.subheader("📊 Reporte de Horas Extra")
                st.dataframe(df)

                # Botón descargar Excel
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
            st.warning("⚠️ Complete todos los campos.")
