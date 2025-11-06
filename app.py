import streamlit as st
from firebase_config import get_firestore_client, check_secrets
from gemini_client import get_gemini_model, generate_text
import datetime

# --- Configuración de la Página ---
st.set_page_config(
    page_title="SAVA RPA Dashboard",
    page_icon="🤖",
    layout="wide"
)

# --- Verificación de Secretos (¡Importante!) ---
# Esto se ejecuta primero para asegurar que la app tenga credenciales.
check_secrets()

# --- Carga de Clientes (Cacheado) ---
try:
    db = get_firestore_client()
    model = get_gemini_model()
except Exception as e:
    st.error(f"Error fatal al inicializar servicios: {e}")
    st.stop()

# --- Título y UI ---
st.title("🤖 Plataforma de Asistencia RPA SAVA")
st.caption("Integración de Streamlit, Firebase (Firestore) y Gemini AI.")

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
            # NOTA: En una app real, usarías onSnapshot (streaming) o paginación.
            # Para Streamlit, .get() es lo más simple.
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

# === Columna 2: Asistente Gemini AI ===
with col2:
    st.header("Asistente IA (Gemini)")
    st.markdown("Basado en el *Canvas* de SAVA, este asistente puede ayudar a generar scripts o analizar logs.")
    
    prompt_context = """
    Eres 'SAVA', un asistente experto en Python y RPA para retail,
    especializado en sistemas legacy como AS/400 y ERPs.
    Tu objetivo es ayudar al desarrollador a crear flujos de automatización.
    (Contexto del Canvas: El objetivo es conectar sistemas legacy con plataformas
    modernas como Shopify, y procesar facturas (IDP)).
    """
    
    user_query = st.text_area("¿En qué necesitas ayuda? (ej. 'Dame un script Python para conectar a un SFTP y descargar un CSV')", height=150)
    
    if st.button("Generar Respuesta"):
        if not user_query:
            st.warning("Por favor, introduce una consulta.")
        elif model:
            full_prompt = f"{prompt_context}\n\n**Consulta del Desarrollador:**\n{user_query}"
            
            with st.spinner("El asistente SAVA está pensando..."):
                response_text = generate_text(full_prompt, model)
            
            if response_text:
                st.markdown(response_text)
            else:
                st.error("No se pudo generar una respuesta.")
        else:
            st.error("Modelo Gemini no disponible.")
