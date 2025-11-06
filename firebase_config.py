import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Nombre de la app de Firebase para evitar reinicializaciones
FIREBASE_APP_NAME = "sava-rpa-platform"

def check_secrets():
    """Verifica que los secretos necesarios estén presentes en Streamlit."""
    required_secrets = ["firebase_credentials", "gemini"]
    if not all(secret in st.secrets for secret in required_secrets):
        st.error("Error: Faltan secretos de configuración (firebase_credentials o gemini).")
        st.stop()
    
    if "api_key" not in st.secrets["gemini"]:
        st.error("Error: Falta 'api_key' en [gemini_secrets].")
        st.stop()

@st.cache_resource
def init_firebase():
    """
    Inicializa la aplicación de Firebase Admin SDK usando las credenciales
    de st.secrets. Devuelve la aplicación inicializada.
    """
    try:
        # Verifica si la app ya está inicializada
        if FIREBASE_APP_NAME in firebase_admin._apps:
            return firebase_admin.get_app(FIREBASE_APP_NAME)

        # Carga las credenciales desde los secretos de Streamlit
        # st.secrets["firebase_credentials"] es un dict (parseado del TOML)
        creds_dict = st.secrets["firebase_credentials"]
        
        # Firebase espera la clave privada con saltos de línea literales
        # Asegurándonos de que el formato sea correcto
        if "private_key" in creds_dict:
             creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        cred = credentials.Certificate(creds_dict)
        
        # Inicializa la app
        app = firebase_admin.initialize_app(cred, name=FIREBASE_APP_NAME)
        st.success("Conexión con Firebase establecida.", icon="🔥")
        return app

    except ValueError as e:
        # Maneja el error común de inicialización
        if "The default Firebase app already exists" in str(e):
            return firebase_admin.get_app(name=FIREBASE_APP_NAME)
        st.error(f"Error al inicializar Firebase: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error desconocido en Firebase: {e}")
        st.stop()

def get_firestore_client():
    """
    Obtiene una instancia del cliente de Firestore.
    Asegura que Firebase esté inicializado primero.
    """
    app = init_firebase()
    if app:
        return firestore.client(app)
    return None
