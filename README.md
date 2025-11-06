Plataforma de Asistencia RPA SAVA (Streamlit + Firebase + Gemini)

Este proyecto es el esqueleto de una aplicación Python que integra Streamlit como frontend, Firebase (Firestore) como base de datos y la API de Gemini como asistente de IA.

1. Estructura del Proyecto

/
|-- .gitignore           # Esencial: Ignora archivos sensibles y de entorno
|-- requirements.txt     # Lista de dependencias de Python
|-- firebase_config.py   # Módulo para inicializar y gestionar la conexión a Firebase
|-- gemini_client.py     # Módulo para gestionar la API de Gemini
|-- app.py               # Aplicación principal de Streamlit


2. Configuración de Credenciales (Crítico)

Este proyecto está diseñado para ser desplegado en Streamlit Cloud y utiliza st.secrets para gestionar las credenciales de forma segura. Nunca subas tus archivos de credenciales a GitHub.

A. Firebase (Service Account)

Ve a tu proyecto de Firebase -> Configuración del proyecto -> Cuentas de servicio.

Haz clic en "Generar nueva clave privada".

Se descargará un archivo json. No le cambies el nombre y no lo subas a GitHub.

El contenido de este archivo json se copiará en los secretos de Streamlit.

B. Gemini (API Key)

Ve a Google AI Studio (o tu consola de Google Cloud) y genera una API Key para la API de Gemini.

C. Configuración de Streamlit Secrets

Para despliegue en Streamlit Cloud:

En el dashboard de tu aplicación en Streamlit Cloud, ve a "Settings" -> "Secrets".

Copia el contenido completo de tu archivo json de Firebase y pégalo. Debe estar formateado como un objeto TOML bajo el namespace [firebase_credentials].

Añade tu clave de Gemini bajo el namespace [gemini].

Tu archivo de secretos en Streamlit Cloud debe verse así:

# Secretos de Firebase (copia y pega el contenido de tu JSON)
[firebase_credentials]
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\ntu-clave-privada\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-.....@tu-project-id.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "[https://accounts.google.com/o/oauth2/auth](https://accounts.google.com/o/oauth2/auth)"
token_uri = "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
auth_provider_x509_cert_url = "[https://www.googleapis.com/oauth2/v1/certs](https://www.googleapis.com/oauth2/v1/certs)"
client_x509_cert_url = "[https://www.googleapis.com/robot/v1/metadata/](https://www.googleapis.com/robot/v1/metadata/)..."

# Secreto de Gemini
[gemini]
api_key = "tu-gemini-api-key"


Para desarrollo local:

Crea un archivo en .streamlit/secrets.toml y pega el mismo contenido de arriba.

3. Advertencia de Seguridad de Firebase

Antes de desplegar, asegúrate de que tus Reglas de Seguridad de Firestore estén configuradas correctamente. Para empezar, puedes usar el modo de desarrollo (permite leer/escribir durante 30 días), pero para producción, debes implementar reglas que solo permitan el acceso a usuarios autenticados.

Ejemplo de reglas (solo permitir usuarios autenticados):

rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}


4. Instrucciones de GitHub (Inicialización)

Estas son las instrucciones paso a paso para inicializar tu repositorio y subir este código base.

Crea un nuevo repositorio en GitHub:
Ve a GitHub.com y crea un nuevo repositorio (ej. sava-rpa-platform). No lo inicialices con un README o .gitignore (ya que nosotros los estamos proporcionando).

Inicializa Git localmente:
Abre tu terminal, navega a la carpeta de este proyecto y ejecuta:

git init -b main


Añade los archivos al "staging":
(Asegúrate de que firebase-service-account.json NO esté en esta carpeta, o que esté listado en .gitignore).

git add .


Realiza tu primer commit:

git commit -m "Initial commit: SAVA platform structure (Streamlit, Firebase, Gemini)"


Conecta tu repositorio local con GitHub:
Reemplaza TU_USUARIO y TU_REPO con los valores de tu repositorio de GitHub.

git remote add origin [https://github.com/TU_USUARIO/TU_REPO.git](https://github.com/TU_USUARIO/TU_REPO.git)


Sube (push) tu código a GitHub:

git push -u origin main


5. Ejecución

Asegúrate de haber instalado las dependencias:

pip install -r requirements.txt


Ejecuta la aplicación localmente:

streamlit run app.py
