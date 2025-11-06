import streamlit as st
import google.generativeai as genai
import time

# Usamos cache_resource para el modelo, así no se recarga en cada run
@st.cache_resource
def get_gemini_model():
    """
    Configura y devuelve el modelo generativo de Gemini.
    """
    try:
        api_key = st.secrets["gemini"]["api_key"]
        genai.configure(api_key=api_key)
        
        # Modelo especificado
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        return model
    except Exception as e:
        st.error(f"Error al configurar Gemini: {e}")
        st.stop()

def generate_text(prompt: str, model):
    """
    Genera texto usando el modelo Gemini, con reintentos simples.
    """
    # Placeholder para la lógica de reintento (backoff exponencial)
    max_retries = 3
    delay = 2
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.warning(f"Error en la API de Gemini (Intento {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1)) # Backoff exponencial simple
            else:
                st.error("No se pudo obtener respuesta de Gemini después de varios intentos.")
                return None
