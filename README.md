# Asistente Alessandro

Asistente virtual diseñado para proporcionar información resumida sobre figuras públicas utilizando tecnologías de Azure Cognitive Services.

## Funcionalidades

- Reconocimiento de voz para recibir preguntas relacionadas con figuras públicas.
- Detección de contenido ofensivo en la consulta de voz.
- Búsqueda y resumen de información detallada sobre figuras públicas utilizando Knowledge Graph API.
- Síntesis de voz para responder preguntas con información relevante y resumida.

## Tecnologías Utilizadas

- Azure Speech SDK para el reconocimiento y síntesis de voz.
- Azure Text Analytics para el análisis de sentimiento y la extracción de entidades.
- Azure Content Safety para la detección de contenido ofensivo.
- Knowledge Graph Search API para obtener información sobre figuras públicas.

## Configuración del Proyecto

Para ejecutar este proyecto, es necesario configurar las siguientes variables de entorno en un archivo `env.txt`:

LANGUAGE_ENDPOINT=Tu_Endpoint_De_Language_Service
LANGUAGE_KEY=Tu_Clave_De_Language_Service
CONTENT_SAFETY_ENDPOINT=Tu_Endpoint_De_Content_Safety_Service
CONTENT_SAFETY_KEY=Tu_Clave_De_Content_Safety_Service
SPEECH_KEY=Tu_Clave_De_Speech_Service
SPEECH_REGION=Tu_Región_De_Speech_Service
API_GOOGLE_KEY=Tu_Clave_API_Google

## Creación del Entorno de Anaconda
Para recrear el entorno de Anaconda especificado para este proyecto, asegúrate de tener Anaconda o Miniconda instalado y sigue estos pasos:

1. Abre una terminal (en Windows, abre el Anaconda Prompt desde el menú de inicio).
2. Navega al directorio que contiene tu archivo environment.yaml.
3. Ejecuta el siguiente comando para crear un nuevo entorno de Anaconda con el nombre cognitive-services:
<code>conda env create -f environment.yaml</code>
4. Una vez que la creación del entorno se haya completado, activa el nuevo entorno con:
<code>conda activate cognitive-services</code>
5. Ahora puedes ejecutar el script alessandro.py dentro de este entorno activado.

## Uso
Para iniciar el asistente, asegúrate de que el entorno cognitive-services esté activado y ejecuta el siguiente comando en tu terminal:

<code>python alessandro.py</code>

Sigue las instrucciones en pantalla para interactuar con el asistente.