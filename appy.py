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
    st.write(f"👤 Usuario: {st.session_state.usuario}")

tiendas = {
    "Piso 2 cafeteria": {
        "Bebidas": ["Inca Kola", "Chicha Morada", "Emoliente", "Sprite", "Coca-Cola", "Fanta"],
        "Entrantes": ["Ceviche", "Papa a la Huancaína", "Anticuchos"],
        "Novedades": ["Quinoa Salad", "Tacu Tacu Burger"],
        "Ofertas": ["Lomo Saltado", "Ají de Gallina"]
    },
    "Piso 6 cafeteria": {
        "Bebidas": ["Pisco Sour", "Chicha Morada", "Inca Kola"],
        "Entrantes": ["Ceviche Clasico", "Leche de Tigre"],
        "Principales": ["Arroz con Mariscos", "Tiradito"],
        "Postres": ["Suspiro a la Limeña", "Mazamorra Morada"]
    },
    "Picantería Andina": {
        "Platos Fuertes": ["Rocoto Relleno", "Cuy Chactado", "Carapulcra"],
        "Bebidas": ["Chicha de Jora", "Emoliente"],
        "Entrantes": ["Papa Rellena", "Tamales"],
        "Postres": ["Helado de Quinua", "Alfajores"]
    },
    "La Sanguchería": {
        "Sandwiches": ["Chicharrón", "Pan con Pollo", "Butifarra"],
        "Bebidas": ["Inca Kola", "Coca-Cola", "Fanta"],
        "Complementos": ["Papas Fritas", "Ensalada"],
        "Ofertas": ["Combo Sanguches + Bebida"]
    },
    "Dulce Tentación": {
        "Postres": ["Tres Leches", "Picarones", "Alfajores", "Helado"],
        "Bebidas": ["Café", "Chocolate Caliente", "Inca Kola"],
        "Novedades": ["Brownie con Quinua"],
        "Ofertas": ["Promo 2x1 Helados"]
    },
    "Snack Express": {
        "Snacks": ["Chips de Yuca", "Maní Salado", "Canchita", "Galletas"],
        "Bebidas": ["Gaseosa", "Agua Mineral", "Jugo Natural"],
        "Ofertas": ["Combo Snack + Bebida"]
    },
    "Veggie Perú": {
        "Entrantes": ["Causa Limeña", "Ensalada de Quinoa"],
        "Platos Principales": ["Tacu Tacu Vegano", "Ají de Gallina Vegano"],
        "Bebidas": ["Jugo Verde", "Chicha Morada"],
        "Postres": ["Mousse de Maracuyá"]
    }
}

planes = {
    "Plan Básico": {
        "precio": 3.00,
        "descripcion": [
            "Ideal para estudiantes que solo desean ver el menú diario y acceder a funciones básicas.",
            "Visualización anticipada del menú del día",
            "Acceso a notificaciones de disponibilidad",
            "Sugerencias personalizadas según historial",
            "Estadísticas de consumo",
            "Personalización de menú o alertas",
            "“Comer informado, pero sin compromiso”"
        ],
    },
    "Plan Smart QOMI": {
        "precio": 4.00,
        "descripcion": [
            "Espacios ideales para disfrutar de la comida. Mejore su experiencia gastronómica con nosotros.",
            "Un menú variado para todos los gustos",
            "Alerta de platos preferidos disponibles",
            "Cancelación/modificación de reservas",
            "Compatible con correo electrónico",
            "“Tu menú, tu tiempo, tu impacto”"
        ],
    }
}

menu_general = []
id_counter = 1
for tienda, categorias in tiendas.items():
    for categoria, productos in categorias.items():
        for producto in productos:
            menu_general.append({
                "id": id_counter,
                "nombre": producto,
                "categoria": categoria,
                "tienda": tienda,
                "precio": round(1 + id_counter * 0.7, 2) 
            })
            id_counter += 1
menu_general = pd.DataFrame(menu_general)

st.markdown(f"## 👋 Bienvenido, {st.session_state.usuario.capitalize()} | 🍽️ QOMI")

st.sidebar.header("🛒 Tu Pedido")
st.sidebar.write(f" Usuario: {st.session_state.usuario}")

if st.session_state.cart:
    carrito_df = pd.DataFrame(st.session_state.cart)
    total = carrito_df["precio"].sum()
    st.sidebar.dataframe(carrito_df[["nombre", "precio"]])
    st.sidebar.markdown(f"**Total: S/. {total:.2f}**")
else:
    total = 0
    st.sidebar.info("Agrega productos para reservar")

hora_actual = datetime.now().replace(second=0, microsecond=0)
hora_min = (hora_actual + timedelta(minutes=30)).time()
hora_max = (hora_actual + timedelta(hours=12)).time()

hora_recojo = st.sidebar.time_input(
    "Elige tu hora de recojo",
    value=hora_min
)

if hora_recojo < hora_min or hora_recojo > hora_max:
    st.sidebar.error(f"La hora debe estar entre {hora_min.strftime('%H:%M')} y {hora_max.strftime('%H:%M')}")
    boton_confirmar = False
else:
    boton_confirmar = st.sidebar.button("Confirmar Reserva")

if boton_confirmar:
    if not st.session_state.cart:
        st.sidebar.warning("Agrega productos antes de confirmar reserva")
    else:
        # Verificar stock para cada producto
        error_stock = False
        for item in st.session_state.cart:
            nombre = item["nombre"]
            if nombre in df_stock["producto"].values:
                stock_disponible = df_stock[df_stock["producto"] == nombre]["stock"].values[0]
                if stock_disponible <= 0:
                    st.sidebar.error(f"Producto sin stock: {nombre}")
                    error_stock = True
            else:
                st.sidebar.error(f"No se encuentra el producto en stock: {nombre}")
                error_stock = True

        if not error_stock:
            # Descontar stock
            for item in st.session_state.cart:
                nombre = item["nombre"]
                df_stock.loc[df_stock["producto"] == nombre, "stock"] -= 1
            df_stock.to_excel(STOCK_PATH, index=False)

            # Continuar con la reserva
            reserva = {
                "usuario": st.session_state.usuario,
                "items": st.session_state.cart.copy(),
                "total": total,
                "hora": hora_recojo.strftime("%H:%M"),
                "fecha": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.reservas.append(reserva)

            if os.path.exists(EXCEL_PATH):
                historial = pd.read_excel(EXCEL_PATH)
            else:
                historial = pd.DataFrame()

            nueva_reserva = pd.DataFrame([{**reserva, "productos": ", ".join([i["nombre"] for i in reserva["items"]])}])
            nueva_reserva.drop(columns=["items"], inplace=True)
            historial = pd.concat([historial, nueva_reserva], ignore_index=True)
            historial.to_excel(EXCEL_PATH, index=False)

            st.success(f"Reserva confirmada para las {hora_recojo.strftime('%H:%M')}.")
            st.session_state.cart = []


seccion = st.sidebar.radio("Navegación", ["Inicio", "Tienda", "Precio", "Ayuda", "Reserva", "Contáctenos"])

if seccion == "Inicio":
    st.title("🏠 Bienvenido a QOMI")
    st.write("""
    QOMI es tu plataforma para reservar platos deliciosos y disfrutar de las mejores bebidas típicas de Perú, además de otras opciones reconocidas mundialmente.
    
    Usa el menú lateral para navegar entre las secciones: Explora nuestras tiendas, elige un plan de suscripción, haz reservas y contáctanos.
    """)

elif seccion == "Tienda":
    st.title("🛍️ Nuestra Tienda - Bebidas y Platos")
    st.write("Selecciona una tienda para explorar sus categorías y productos:")

    tienda_sel = st.selectbox("Elige la tienda", list(tiendas.keys()))

    if tienda_sel:
        categorias = tiendas[tienda_sel]
        for categoria, productos in categorias.items():
            with st.expander(f"{categoria} ({len(productos)} productos)"):
                for producto in productos:
                    col1, col2 = st.columns([6,1])
                    with col1:
                        st.write(f"**{producto}**")
                    with col2:
                        if st.button(f"Agregar {producto}", key=f"agregar_{tienda_sel}_{categoria}_{producto}"):
                            prod_df = menu_general[(menu_general["nombre"]==producto) & (menu_general["tienda"]==tienda_sel)]
                            if not prod_df.empty:
                                st.session_state.cart.append(prod_df.iloc[0].to_dict())
                                st.success(f"Agregado {producto} al pedido")

elif seccion == "Precio":
    st.title("💰 Nuestros Planes de Suscripción")
    for nombre_plan, info in planes.items():
        st.subheader(nombre_plan)
        st.write(f"**Precio:** S/. {info['precio']:.2f} al mes")
        for linea in info["descripcion"]:
            st.markdown(f"- {linea}")

        if st.button(f"Comprar {nombre_plan}", key=f"btn_comprar_{nombre_plan}"):
            st.info(f"Has seleccionado el {nombre_plan}. En proceso de integración de pago.")

elif seccion == "Ayuda":
    st.title("❓ Ayuda y Consultas")

    st.write("¿Tienes alguna duda o comentario? Déjanos tu mensaje aquí:")

    with st.form("form_ayuda", clear_on_submit=True):
        nombre = st.text_input("Nombre")
        email = st.text_input("Correo electrónico")
        mensaje = st.text_area("Comentario o consulta")
        enviar = st.form_submit_button("Enviar")

        if enviar:
            if not (nombre and email and mensaje):
                st.warning("Por favor completa todos los campos.")
            else:
                # Guardar en Excel
                if os.path.exists(HELP_PATH):
                    df_comentarios = pd.read_excel(HELP_PATH)
                else:
                    df_comentarios = pd.DataFrame(columns=["Nombre", "Correo", "Mensaje", "Fecha"])

                nueva_consulta = pd.DataFrame([{
                    "Nombre": nombre,
                    "Correo": email,
                    "Mensaje": mensaje,
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])

                df_comentarios = pd.concat([df_comentarios, nueva_consulta], ignore_index=True)
                df_comentarios.to_excel(HELP_PATH, index=False)

                st.success("Gracias por tu mensaje. Te responderemos pronto.")

elif seccion == "Reserva":
    st.title("📅 Tus Reservas")

    if st.session_state.reservas:
        for i, reserva in enumerate(st.session_state.reservas):
            pago_url = "https://www.paypal.com"
            st.markdown(
                f'<a href="{pago_url}" target="_blank"><button style="background-color:#0070BA;color:white;padding:6px 12px;border:none;border-radius:5px;">Ir a Pagar en PayPal</button></a>',
                unsafe_allow_html=True
            )

            st.markdown(f"**Reserva #{i+1}**")
            st.write(f"Fecha: {reserva['fecha']}")
            st.write(f"Hora: {reserva['hora']}")
            st.write(f"Productos:")
            for item in reserva['items']:
                st.write(f"- {item['nombre']} (S/. {item['precio']:.2f})")
            st.write(f"**Total:** S/. {reserva['total']:.2f}")
            st.markdown("---")
    else:
        st.info("No tienes reservas confirmadas aún.")

elif seccion == "Contáctenos":
    st.title("📞 Contáctanos")

    st.write("""
    Puedes comunicarte con nosotros a través de los siguientes medios:

    - 📧 Email: contacto@qomi.pe  
    - 📞 Teléfono: +51 947 651 798  
    - 🏢 Dirección: Av. Lima 123, Miraflores, Lima, Perú

    También puedes enviarnos un mensaje directo en la sección Ayuda.
    """)

if st.sidebar.button("Cerrar sesión"):
    st.session_state.usuario = None
    st.rerun()
