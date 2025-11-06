import streamlit as st
from firebase_config import get_firestore_client, check_secrets
from gemini_client import GeminiUtils  # Importar la nueva clase
from PIL import Image  # Importar Pillow para manejar imágenes
import datetime
import json

# --- Configuración de la Página ---
st.set_page_config(
    page_title="SAVA RPA Dashboard",
    page_icon="🤖",
    layout="wide"
)

# --- Verificación de Secretos (¡Importante!) ---
# Esto se ejecuta primero y detiene la app si faltan secretos.
check_secrets()

# --- Carga de Clientes (Cacheado) ---
# Usamos st.cache_resource para inicializar solo una vez.
try:
    db = get_firestore_client()
    
    @st.cache_resource
    def get_gemini_utils_instance():
        """Función para cachear la instancia de GeminiUtils."""
        return GeminiUtils()
        
    gemini_utils = get_gemini_utils_instance()

except Exception as e:
    # Si la inicialización falla (ej. check_secrets() llama a st.stop()), 
    # esto no se ejecutará, pero es una doble seguridad.
    st.error(f"Error fatal al inicializar servicios: {e}")
    st.stop()

# --- Título y UI ---
st.title("🤖 Plataforma de Asistencia RPA SAVA")
st.caption("Integración de Streamlit, Firebase (Firestore) y Gemini AI (Visión).")

# --- Columnas de la UI ---
col1, col2 = st.columns(2)

# === Columna 1: Interacción con Firebase ===
with col1:
    st.header("Gestor de Tareas (Firestore DB)")
    
    st.subheader("Añadir Nueva Tarea de RPA")
    with st.form("new_task_form", clear_on_submit=True):
        task_description = st.text_input("Descripción de la tarea (ej. 'Sincronizar Inventario AS/400')")
        task_priority = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
        submitted = st.form_submit_button("Añadir Tarea")

    if submitted and task_description:
        if db:
            try:
                # Crear un nuevo documento
                doc_ref = db.collection("rpa_tasks").document()
                task_data = {
                    "description": task_description,
                    "priority": task_priority,
                    "status": "pending",
                    "created_at": datetime.datetime.now(datetime.timezone.utc)
                }
                doc_ref.set(task_data)
                st.success(f"Tarea añadida a Firestore con ID: {doc_ref.id}")
            except Exception as e:
                st.error(f"Error al añadir tarea a Firestore: {e}")
        else:
            st.error("Cliente de Firestore no disponible.")

    st.subheader("Tareas Pendientes en Firebase")
    
    # Mostrar tareas de Firebase
    if db:
        try:
            # Consultamos las tareas pendientes
            tasks_ref = db.collection("rpa_tasks").where("status", "==", "pending")
            tasks = tasks_ref.get() # .get() es una lectura única

            if not tasks:
                st.info("No hay tareas pendientes.")
            
            for task in tasks:
                task_data = task.to_dict()
                st.markdown(f"""
                <div style="border: 1px solid #333; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>{task_data.get('description')}</strong><br>
                    <small>Prioridad: {task_data.get('priority')} | ID: {task.id}</small>
                </div>
                """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error al leer tareas de Firestore: {e}")

# === Columna 2: Asistente Gemini AI (Visión) ===
with col2:
    st.header("Catalogador de Inventario (Gemini)")
    st.markdown("Carga una imagen de un artículo para catalogarlo automáticamente.")
    
    uploaded_image = st.file_uploader("Cargar imagen del artículo...", type=["jpg", "jpeg", "png"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Imagen cargada", use_column_width=True)
        
        # Botón para procesar la imagen
        if st.button("Analizar Imagen"):
            try:
                # Abrir la imagen con Pillow
                image_pil = Image.open(uploaded_image)
                
                with st.spinner("El asistente SAVA está analizando la imagen..."):
                    # Llamar a la nueva función de GeminiUtils
                    json_response = gemini_utils.analyze_image(image_pil, "Artículo de inventario")
                
                st.success("Análisis completado:")
                
                # Parsear el JSON para mostrarlo bonito
                try:
                    data = json.loads(json_response)
                    st.json(data) # Mostrar como un JSON interactivo
                except json.JSONDecodeError:
                    st.error("La IA devolvió un formato inesperado.")
                    st.text(json_response)

            except Exception as e:
                st.error(f"Error al procesar la imagen: {e}")
