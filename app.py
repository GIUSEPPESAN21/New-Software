import streamlit as st
from firebase_config import get_firestore_client, check_secrets
from gemini_client import GeminiUtils  # Importar la nueva clase
from PIL import Image  # Importar Pillow para manejar imágenes
import datetime
import json

# --- Configuración de la Página ---
st.set_page_config(
    page_title="SAVA RPA Dashboard",
    page_icon="https://github.com/GIUSEPPESAN21/LOGO-SAVA/blob/main/LOGO.jpg?raw=true", # Icono de la pestaña del navegador
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
    st.error(f"Error fatal al inicializar servicios: {e}")
    st.stop()

# --- CSS Personalizado para Mejorar el Diseño ---
st.markdown("""
<style>
    /* Contenedores principales */
    .stApp {
        background-color: #F0F2F6; /* Un gris claro para el fondo */
    }

    /* Estilo de los botones */
    .stButton > button {
        border: 2px solid #1E88E5; /* Borde azul SAVA */
        background-color: #1E88E5; /* Fondo azul SAVA */
        color: white;
        padding: 0.5em 1em;
        border-radius: 8px; /* Bordes redondeados */
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        width: 100%; /* Botones de ancho completo */
    }
    .stButton > button:hover {
        background-color: #1565C0; /* Azul más oscuro al pasar el ratón */
        border-color: #1565C0;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        transform: translateY(-2px); /* Efecto de elevación */
    }
    .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Botón de la sidebar (para que coincida) */
    .stSidebar .stButton > button {
        background-color: #FFFFFF;
        color: #1E88E5;
        border: 1px solid #1E88E5;
    }
    .stSidebar .stButton > button:hover {
        background-color: #1E88E5;
        color: #FFFFFF;
        border-color: #1E88E5;
    }

    /* Estilo para los contenedores de las columnas */
    div[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        background-color: white;
        padding: 1.5em;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Títulos */
    h1, h2 {
        color: #1976D2; /* Azul SAVA */
    }
    
    /* Logo en la sidebar */
    [data-testid="stSidebar"] {
        padding-top: 2rem;
    }
    [data-testid="stSidebar"] .stImage {
        text-align: center;
        margin-bottom: 1rem; /* Espacio debajo del logo */
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN (SIDEBAR) ---

# URL del logo de SAVA
LOGO_URL = "https://github.com/GIUSEPPESAN21/LOGO-SAVA/blob/main/LOGO.jpg?raw=true"
st.sidebar.image(LOGO_URL, width=200)

st.sidebar.title("Navegación de SAVA")

# Inicializar el estado de la página
if 'page' not in st.session_state:
    st.session_state.page = "🚀 Dashboard Principal"

# Botones de navegación en la sidebar
if st.sidebar.button("🚀 Dashboard Principal", use_container_width=True):
    st.session_state.page = "🚀 Dashboard Principal"
if st.sidebar.button("🏢 Acerca de SAVA", use_container_width=True):
    st.session_state.page = "🏢 Acerca de SAVA"

# --- Definición de las Páginas ---

def main_dashboard():
    """
    Función para la página principal (el dashboard).
    """
    st.title("🤖 Plataforma de Asistencia RPA SAVA")
    st.caption("Integración de Streamlit, Firebase (Firestore) y Gemini AI (Visión).")

    # --- Columnas de la UI ---
    col1, col2 = st.columns(2, gap="large")

    # === Columna 1: Interacción con Firebase ===
    with col1:
        st.header("Gestor de Tareas (Firestore DB)")
        
        with st.form("new_task_form", clear_on_submit=True):
            st.subheader("Añadir Nueva Tarea de RPA")
            task_description = st.text_input("Descripción de la tarea (ej. 'Sincronizar Inventario AS/400')")
            task_priority = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
            # El botón ahora tomará el estilo CSS
            submitted = st.form_submit_button("Añadir Tarea")

        if submitted and task_description:
            if db:
                try:
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
        
        if db:
            try:
                tasks_ref = db.collection("rpa_tasks").where("status", "==", "pending")
                tasks = tasks_ref.get() 
                if not tasks:
                    st.info("No hay tareas pendientes.")
                
                # Contenedor con scroll para la lista de tareas
                with st.container(height=300):
                    for task in tasks:
                        task_data = task.to_dict()
                        st.markdown(f"""
                        <div style="border: 1px solid #E0E0E0; padding: 10px; border-radius: 8px; margin-bottom: 10px; background-color: #FAFAFA;">
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
            
            # El botón ahora tomará el estilo CSS
            if st.button("Analizar Imagen"):
                try:
                    image_pil = Image.open(uploaded_image)
                    with st.spinner("El asistente SAVA está analizando la imagen..."):
                        json_response = gemini_utils.analyze_image(image_pil, "Artículo de inventario")
                    
                    st.success("Análisis completado:")
                    try:
                        data = json.loads(json_response)
                        st.json(data)
                    except json.JSONDecodeError:
                        st.error("La IA devolvió un formato inesperado.")
                        st.text(json_response)

                except Exception as e:
                    st.error(f"Error al procesar la imagen: {e}")

def about_page():
    """
    Función para la página "Acerca de SAVA"
    Este es el código exacto que tú proporcionaste, con una corrección en la imagen.
    """
    st.title("Sobre SAVA SOFTWARE")
    st.subheader("Innovación y Tecnología para el Retail del Futuro")

    st.markdown("""
    En **SAVA**, somos pioneros en el desarrollo de soluciones de software que fusionan la inteligencia artificial
    con las necesidades reales del sector retail. Nuestra misión es empoderar a los negocios con herramientas
    poderosas, intuitivas y eficientes que transformen sus operaciones y potencien su crecimiento.

    Creemos que la tecnología debe ser un aliado, no un obstáculo. Por eso, diseñamos **OSIRIS** pensando
    en la agilidad, la precisión y la facilidad de uso.
    """)

    st.markdown("---")

    st.subheader("Nuestro Equipo Fundador")

    # Use columns for founder details
    col1_founder, col2_founder = st.columns([1, 3])
    with col1_founder:
        # La URL que diste ("...logo_sava.png") era el logo, no una foto de perfil.
        # He puesto un placeholder. Reemplaza la URL de abajo por la de tu foto.
        st.image("https://placehold.co/200x200/1E88E5/FFFFFF?text=CEO", width=200, caption="CEO")
        
    with col2_founder:
        st.markdown("#### Joseph Javier Sánchez Acuña")
        st.markdown("**CEO - SAVA SOFTWARE FOR ENGINEERING**")
        st.write("""
        Líder visionario con una profunda experiencia en inteligencia artificial y desarrollo de software.
        Joseph es el cerebro detrás de la arquitectura de OSIRIS, impulsando la innovación
        y asegurando que nuestra tecnología se mantenga a la vanguardia.
        """)
        # Links in markdown
        st.markdown(
            """
            - **LinkedIn:** [joseph-javier-sánchez-acuña](https://www.linkedin.com/in/joseph-javier-sánchez-acuña-150410275)
            - **GitHub:** [GIUSEPPESAN21](https://github.com/GIUSEPPESAN21)
            """
        )
    st.markdown("---")

    st.markdown("##### Cofundadores")

    c1_cof, c2_cof, c3_cof = st.columns(3)
    with c1_cof:
        st.info("**Xammy Alexander Victoria Gonzalez**\n\n*Director Comercial*")
    with c2_cof:
        st.info("**Jaime Eduardo Aragon Campo**\n\n*Director de Operaciones*")
    with c3_cof:
        # Assuming Joseph is also the Project Director based on previous code
        st.info("**Joseph Javier Sanchez Acuña**\n\n*Director de Proyecto*")

# --- ENRUTADOR PRINCIPAL DE PÁGINAS ---
# Ejecuta la función de la página seleccionada en st.session_state

if st.session_state.page == "🚀 Dashboard Principal":
    main_dashboard()
elif st.session_state.page == "🏢 Acerca de SAVA":
    about_page()
