import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import base64 # Importar la librería base64

# Nombre de la app de Firebase para evitar reinicializaciones
FIREBASE_APP_NAME = "sava-rpa-platform"

def check_secrets():
    """
    Verifica que los secretos necesarios estén presentes en Streamlit.
    Adaptado al nuevo formato de secrets.toml.
    """
    
    # 1. Verificar la clave de API de Gemini (AHORA EN NIVEL SUPERIOR)
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Error: Falta 'GEMINI_API_KEY' en los secretos de Streamlit.")
        st.stop() # Detiene la ejecución si falta la clave
        
    # 2. Verificar la sección [firebase_credentials] y la clave Base64
    if "firebase_credentials" not in st.secrets or "service_account_base64" not in st.secrets["firebase_credentials"]:
        st.error("Error: Falta la sección [firebase_credentials] o 'service_account_base64' en los secretos.")
        st.stop() # Detiene la ejecución si falta la clave


@st.cache_resource
def init_firebase():
    """
    Inicializa la aplicación de Firebase Admin SDK usando las credenciales
    Base64 de st.secrets. Devuelve la aplicación inicializada.
    """
    try:
        # Verifica si la app ya está inicializada
        if FIREBASE_APP_NAME in firebase_admin._apps:
            return firebase_admin.get_app(FIREBASE_APP_NAME)

        # --- Lógica de decodificación Base64 ---
        # 1. Obtener la cadena Base64 de los secretos
        base64_creds = st.secrets["firebase_credentials"]["service_account_base64"]
        
        # 2. Decodificar la cadena Base64 a bytes
        creds_bytes = base64.b64decode(base64_creds)
        
        # 3. Decodificar los bytes a una cadena JSON
        creds_json_str = creds_bytes.decode('utf-8')
        
        # 4. Cargar la cadena JSON en un diccionario de Python
        creds_dict = json.loads(creds_json_str)
        # --- Fin de la lógica Base64 ---
        
        # El JSON decodificado ya tiene los \n correctos en la clave privada
        cred = credentials.Certificate(creds_dict)
        
        # Inicializa la app
        app = firebase_admin.initialize_app(cred, name=FIREBASE_APP_NAME)
        st.success("Conexión con Firebase establecida (desde Base64).", icon="🔥")
        return app

    except ValueError as e:
        # Maneja el error común de inicialización
        if "The default Firebase app already exists" in str(e):
            return firebase_admin.get_app(name=FIREBASE_APP_NAME)
        st.error(f"Error al inicializar Firebase: {e}")
        st.stop()
    except (json.JSONDecodeError, base64.binascii.Error) as e:
        st.error(f"Error al decodificar las credenciales de Firebase (Base64/JSON): {e}")
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
