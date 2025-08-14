


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
tabs_labels = [
    "Inspección y Control de Recepción de Materias Primas",
    "Registro de Devolución a Proveedores"
]
pestañas = st.tabs(tabs_labels)

# --- Pestaña 1: Inspección y Control de Recepción de Materias Primas ---
with pestañas[0]:
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col1:
        fecha = st.date_input("Fecha", value=date.today(), key="p1_fecha")
    with col2:
        proveedor = st.text_input("Proveedor", key="p1_proveedor")
    with col3:
        factura = st.text_input("Factura N°", key="p1_factura")
    with col4:
        otro = st.text_input(" ", key="p1_otro")

    st.markdown("### Detalle de Productos")
    columnas = [
        "Producto", "Lote", "Fecha Vencimiento", "Temp. (°C)",
        "Características Organolépticas (Color, Olor, Textura)", "Empaque", "Observaciones"
    ]
    filas = st.number_input("Cantidad de productos", min_value=1, max_value=20, value=5, key="p1_filas")
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
                    "", opciones, key=f"p1_prod_{i}_{j}_select"
                )
                if val == "Características organolépticas":
                    val = ""
                valor_carac = val
                fila.append(val)
            elif col == "Fecha Vencimiento":
                val = cols[j].date_input(
                    "", key=f"p1_prod_{i}_{j}_date"
                )
                fila.append(val)
            elif col == "Observaciones":
                if valor_carac == "No cumple":
                    val = cols[j].text_input(
                        "Observaciones", key=f"p1_prod_{i}_{j}_obs", placeholder="Describa la observación"
                    )
                else:
                    val = ""
                fila.append(val)
            else:
                val = cols[j].text_input(
                    col, key=f"p1_prod_{i}_{j}", label_visibility="collapsed", placeholder=col
                )
                fila.append(val)
        data.append(fila)
        st.markdown("<hr style='margin: 0.2em 0; border: 1px solid #e6e6e6;'>", unsafe_allow_html=True)

    st.markdown("### Condiciones del Vehículo de Transporte")
    col5, col6, col7 = st.columns([2, 1, 2])
    with col5:
        limpio = st.radio("¿Vehículo limpio?", ["Sí", "No"], horizontal=True, key="p1_limpio")
    with col6:
        temp_furgon = st.text_input("Temperatura del furgón (°C)", placeholder="°C", key="p1_temp_furgon")
    with col7:
        observaciones = st.text_input("Observaciones adicionales", placeholder="Opcional", key="p1_observaciones_adicionales")

    if st.button("Generar y subir reporte a Dropbox", key="p1_btn_reporte"):
        df = pd.DataFrame(data, columns=columnas)
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
# --- Pestaña 2: Registro de Devolución a Proveedores ---
with pestañas[1]:
    st.header("Formato de Registro de Devolución a Proveedores")

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        fecha_dev = st.date_input("Fecha de Devolución", key="p2_fecha_dev")
    with col2:
        proveedor_dev = st.text_input("Proveedor", key="p2_proveedor")
    with col3:
        otro_dev = st.text_input(" ", key="p2_otro")

    st.markdown("### Detalle de Productos Devueltos")
    columnas_dev = [
        "Producto(s) Devuelto(s)", "Cantidad", "Lote", "Causal del Rechazo (Marcar con X)"
    ]
    filas_dev = st.number_input("Cantidad de productos devueltos", min_value=1, max_value=20, value=3, key="p2_filas")
    data_dev = []
    cols_titulos_dev = st.columns(len(columnas_dev))
    for j, col in enumerate(columnas_dev):
        cols_titulos_dev[j].markdown(f"**{col}**")
    opciones_causal = [
        "Temperatura Inadecuada",
        "Características Organolépticas Alteradas",
        "Empaque Defectuoso",
        "Fecha de Vencimiento Inadecuada",
        "Presencia de Plagas o Contaminantes",
        "Otro"
    ]
    for i in range(filas_dev):
        cols = st.columns(len(columnas_dev))
        fila = []
        for j, col in enumerate(columnas_dev):
            if col == "Causal del Rechazo (Marcar con X)":
                val = cols[j].multiselect(
                    "", opciones_causal, key=f"p2_dev_{i}_{j}_multi"
                )
                val_excel = ", ".join(val)
                fila.append(val_excel)
            else:
                val = cols[j].text_input(
                    col, key=f"p2_dev_{i}_{j}", label_visibility="collapsed", placeholder=col
                )
                fila.append(val)
        data_dev.append(fila)
        st.markdown("<hr style='margin: 0.2em 0; border: 1px solid #e6e6e6;'>", unsafe_allow_html=True)

    st.markdown("**Responsable de la Devolución:** ____________________________  **Firma:** _____________")
    st.markdown("**Nombre del Conductor/Representante del Proveedor:** _____________  **Firma:** _____________")

    if st.button("Generar y subir registro de devolución a Dropbox", key="p2_btn_reporte"):
        df_dev = pd.DataFrame(data_dev, columns=columnas_dev)
        archivo_dev = generar_excel(
            proveedor_dev,
            fecha_dev,
            df_dev,
            "",  # responsable (puedes agregar input si lo deseas)
            "",  # supervisor (no aplica aquí)
            "",  # revision (no aplica aquí)
            nombre_reporte="Registro_Devolucion_Proveedores"
        )
        url_dev = subir_a_dropbox(archivo_dev)
        st.success(f"Registro generado y subido. Acceso: {url_dev}")
    #
        url = subir_a_dropbox(archivo)
        st.success(f"Reporte generado y subido. Acceso: {url}")