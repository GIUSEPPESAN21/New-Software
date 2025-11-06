import google.generativeai as genai
import logging
from PIL import Image
import streamlit as st
import json

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiUtils:
    def __init__(self):
        """
        Inicializa el cliente de Gemini.
        Lee la API key desde el nivel superior de st.secrets.
        """
        # Lee la API Key del nivel superior de los secrets
        self.api_key = st.secrets.get('GEMINI_API_KEY')
        if not self.api_key:
            # Si falta la clave, detener la app con un error claro
            st.error("Error: GEMINI_API_KEY no encontrada en los secrets de Streamlit.")
            st.stop()
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = self._get_available_model()
        except Exception as e:
            st.error(f"Error al configurar Gemini con la API Key: {e}")
            st.stop()
    
    def _get_available_model(self):
        """
        Intenta inicializar el mejor modelo de Gemini disponible de la lista proporcionada.
        """
        # Lista de modelos priorizada
        model_candidates = [
            "gemini-1.5-flash-latest",    # Versión más reciente y rápida de 1.5
            "gemini-1.5-pro-latest",      # Versión Pro más reciente de 1.5
            "gemini-1.5-flash",           # Modelo Flash básico
            "gemini-1.5-pro",             # Modelo Pro básico
        ]
        
        for model_name in model_candidates:
            try:
                # Comprueba si el modelo existe y está disponible
                model = genai.GenerativeModel(model_name)
                logger.info(f"✅ Modelo de visión '{model_name}' inicializado con éxito.")
                return model
            except Exception as e:
                logger.warning(f"⚠️ Modelo '{model_name}' no disponible o no compatible: {e}")
                continue
        
        # Si el bucle termina sin un modelo, detener la app
        st.error("No se pudo inicializar ningún modelo de visión de Gemini compatible. Verifica tu API Key y los permisos.")
        st.stop()
    
    def analyze_image(self, image_pil: Image, description: str = ""):
        """
        Analiza una imagen y devuelve una respuesta JSON estructurada y limpia.
        """
        if not self.model:
            st.error("El modelo Gemini no está inicializado.")
            return json.dumps({"error": "El modelo Gemini no está inicializado."})

        try:
            # Prompt optimizado para forzar una salida JSON limpia y detallada.
            prompt = f"""
            Analiza esta imagen de un objeto de inventario.
            Descripción adicional del sistema de detección: "{description}"
            
            Actúa como un experto catalogador. Tu única salida debe ser un objeto JSON válido con estas claves:
            - "elemento_identificado": (string) El nombre específico y descriptivo del objeto.
            - "cantidad_aproximada": (integer) El número de unidades que ves. Si es solo uno, pon 1.
            - "estado_condicion": (string) La condición aparente (ej: "Nuevo en empaque", "Usado, con ligeras marcas", "Componente individual").
            - "caracteristicas_distintivas": (string) Una lista separada por comas de características visuales clave (ej: "Color rojo, carcasa metálica, conector USB-C").
            - "posible_categoria_de_inventario": (string) La categoría más lógica (ej: "Componentes Electrónicos", "Ferretería", "Material de Oficina").
            - "marca_modelo_sugerido": (string) Si es visible, la marca y/o modelo del objeto (ej: "Sony WH-1000XM4"). Si no, pon "No visible".

            IMPORTANTE: Responde solo con el objeto JSON, sin texto adicional, explicaciones, ni las marcas ```json.
            """
            
            response = self.model.generate_content([prompt, image_pil])
            
            # Limpieza robusta de la respuesta para extraer solo el JSON.
            if response and response.text:
                clean_text = response.text.strip()
                
                # Busca el inicio y fin del JSON
                json_start = clean_text.find('{')
                json_end = clean_text.rfind('}') + 1
                
                if json_start != -1 and json_end != 0:
                    json_str = clean_text[json_start:json_end]
                    # Validar si es un JSON válido antes de devolver
                    try:
                        # Intenta cargar el JSON para validar
                        json.loads(json_str) 
                        return json_str # Devuelve la cadena JSON válida
                    except json.JSONDecodeError:
                        logger.error(f"La IA devolvió un JSON mal formado. Raw: {clean_text}")
                        return json.dumps({"error": "La IA devolvió un JSON mal formado.", "raw_response": clean_text})
                else:
                    logger.error(f"No se encontró un JSON en la respuesta de la IA. Raw: {clean_text}")
                    return json.dumps({"error": "No se encontró un objeto JSON en la respuesta de la IA.", "raw_response": clean_text})
            else:
                logger.error("La IA no devolvió una respuesta válida (vacía).")
                return json.dumps({"error": "La IA no devolvió una respuesta válida."})
                
        except Exception as e:
            logger.error(f"Error crítico durante el análisis de imagen con Gemini: {e}")
            st.error(f"Error en la API de Gemini: {e}")
            return json.dumps({"error": f"No se pudo contactar al servicio de IA: {str(e)}"})
