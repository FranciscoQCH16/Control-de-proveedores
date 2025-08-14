


import streamlit as st
import pandas as pd
from utils.excel import generar_excel
from utils.dropbox import subir_a_dropbox
from datetime import date

# --- Autenticación usando secrets de Streamlit ---
USUARIOS_AUTORIZADOS = dict(st.secrets["auth"]) if "auth" in st.secrets else {}

def login():
    st.title("Iniciar sesión")
    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        if usuario in USUARIOS_AUTORIZADOS and password == USUARIOS_AUTORIZADOS[usuario]:
            st.session_state["autenticado"] = True
            try:
                st.rerun()
            except AttributeError:
                pass
        else:
            st.error("Usuario o contraseña incorrectos")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    login()
    st.stop()

st.set_page_config(page_title="Control de Proveedores", layout="wide")

st.title("Sistema de Reportes L & D")

# Pestaña única: Inspección y control de recepción de materias primas
tabs_labels = ["Inspección y Control de Recepción de Materias Primas"]
pestañas = st.tabs(tabs_labels)
with pestañas[0]:
    st.header("Formato de Inspección y Control de Recepción de Materias Primas")

    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col1:
        fecha = st.date_input("Fecha", value=date.today())
    with col2:
        proveedor = st.text_input("Proveedor")
    with col3:
        factura = st.text_input("Factura N°")


    st.markdown("### Detalle de Productos")
    columnas = [
        "Producto", "Lote", "Fecha Vencimiento", "Temp. (°C)",
        "Características Organolépticas (Color, Olor, Textura)", "Empaque", "Observaciones"
    ]
    filas = st.number_input("Cantidad de productos", min_value=1, max_value=20, value=5)
    data = []
    cols_titulos = st.columns(len(columnas))
    for j, col in enumerate(columnas):
        cols_titulos[j].markdown(f"**{col}**")
    for i in range(filas):
        cols = st.columns(len(columnas))
        fila = []
        valor_carac = ""
        for j, col in enumerate(columnas):
            if col == "Características Organolépticas (Color, Olor, Textura)":
                opciones = ["Características organolépticas", "Cumple", "No cumple"]
                val = cols[j].selectbox(
                    "", opciones, key=f"prod_{i}_{j}_select"
                )
                if val == "Características organolépticas":
                    val = ""
                valor_carac = val
                fila.append(val)
            elif col == "Fecha Vencimiento":
                val = cols[j].date_input(
                    "", key=f"prod_{i}_{j}_date"
                )
                fila.append(val)
            elif col == "Observaciones":
                if valor_carac == "No cumple":
                    val = cols[j].text_input(
                        "Observaciones", key=f"prod_{i}_{j}_obs", placeholder="Describa la observación"
                    )
                else:
                    val = ""
                fila.append(val)
            else:
                val = cols[j].text_input(
                    col, key=f"prod_{i}_{j}", label_visibility="collapsed", placeholder=col
                )
                fila.append(val)
        data.append(fila)
        st.markdown("<hr style='margin: 0.2em 0; border: 1px solid #e6e6e6;'>", unsafe_allow_html=True)
    df = pd.DataFrame(data, columns=columnas)

    st.markdown("### Condiciones del Vehículo de Transporte")
    col5, col6, col7 = st.columns([2, 1, 2])
    with col5:
        limpio = st.radio("¿Vehículo limpio?", ["Sí", "No"], horizontal=True)
    with col6:
        temp_furgon = st.text_input("Temperatura del furgón (°C)", placeholder="°C")
    with col7:
        observaciones = st.text_input("Observaciones adicionales", placeholder="Opcional")

    if st.button("Generar y subir reporte a Dropbox"):
        archivo = generar_excel(
            proveedor,
            fecha,
            df,
            limpio,
            factura,
            temp_furgon,
            nombre_reporte="Inspeccion_Recepcion_Materias_Primas"
        )
        url = subir_a_dropbox(archivo)
        st.success(f"Reporte generado y subido. Acceso: {url}")