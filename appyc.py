
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import os

st.set_page_config(page_title="QOMI - Reservas de Comida", layout="wide")

st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
        background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
        color: #333;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.4em 1em;
    }
    .stButton>button:hover {
        background-color: #45a049;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

EXCEL_PATH = "base_datos_reservas.xlsx"
USUARIOS_PATH = "usuarios.xlsx"
HELP_PATH = "comentarios_ayuda.xlsx"
STOCK_PATH = "stock_restaurantes.xlsx"

if os.path.exists(STOCK_PATH):
    df_stock = pd.read_excel(STOCK_PATH)
else:
    df_stock = pd.DataFrame(columns=["producto", "stock"])
    df_stock.to_excel(STOCK_PATH, index=False)

if os.path.exists(USUARIOS_PATH):
    df_usuarios = pd.read_excel(USUARIOS_PATH)
else:
    df_usuarios = pd.DataFrame(columns=["usuario", "password_hash"])
    df_usuarios.to_excel(USUARIOS_PATH, index=False)

if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "cart" not in st.session_state:
    st.session_state.cart = []
if "reservas" not in st.session_state:
    st.session_state.reservas = []
if "comentarios" not in st.session_state:
    st.session_state.comentarios = []

def autenticar(usuario, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user = df_usuarios[df_usuarios["usuario"] == usuario]
    return not user.empty and user.iloc[0]["password_hash"] == password_hash

if not st.session_state.usuario:
    opcion = st.selectbox("¿Tienes cuenta?", ["Iniciar sesión", "Registrarse"])

    if opcion == "Iniciar sesión":
        st.markdown("<h2 style='text-align:center; margin-top:50px;'>🔐 Inicia Sesión</h2>", unsafe_allow_html=True)
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            if autenticar(usuario, password):
                st.session_state.usuario = usuario
                st.success("Acceso correcto")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        st.stop()
    else:
        st.markdown("<h2 style='text-align:center; margin-top:50px;'>📝 Regístrate</h2>", unsafe_allow_html=True)
        nuevo_usuario = st.text_input("Elige un nombre de usuario")
        nueva_password = st.text_input("Crea una contraseña", type="password")
        if st.button("Registrar cuenta"):
            if nuevo_usuario in df_usuarios["usuario"].values:
                st.warning("El nombre de usuario ya existe. Elige otro.")
            elif nuevo_usuario and nueva_password:
                nuevo_hash = hashlib.sha256(nueva_password.encode()).hexdigest()
                df_usuarios = pd.concat([
                    df_usuarios,
                    pd.DataFrame([[nuevo_usuario, nuevo_hash]], columns=["usuario", "password_hash"])
                ], ignore_index=True)
                df_usuarios.to_excel(USUARIOS_PATH, index=False)
                st.success("Usuario registrado correctamente. Ahora puedes iniciar sesión.")
            else:
                st.warning("Debes llenar ambos campos para registrarte.")
        st.stop()

with st.sidebar:
    st.image("logo_qomi.jpeg", width=120)
    st.markdown("### QOMI")
    st.write(f"👤 Usuario: {st.session_state.usuario or 'Invitado'}")

usuario = st.session_state.usuario if st.session_state.usuario else "invitado"
st.markdown(f"## 👋 Bienvenido, {usuario.capitalize()} | 🍽️ QOMI")
