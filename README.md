# Seguritos - Chatbot de Seguros para LATAM

Chatbot de inteligencia artificial especializado en el mercado asegurador de LATAM. Responde consultas sobre seguros, busca noticias relevantes en la web y sugiere optimizaciones de pólizas.

## Estructura del proyecto

```
Insurance_Chatbot/
├── main.py                             # Punto de entrada (Chainlit)
├── ingest.py                           # Script de ingesta de PDFs en ChromaDB
├── config/
│   └── settings.py                     # Configuración: LLM, embeddings, vector DB
├── prompts/
│   ├── classification_prompt.py        # Prompt de clasificación de consultas
│   └── conversation_prompt.py          # Prompts de conversación, RAG, búsqueda web y optimización
├── chains/
│   ├── classification_chain.py         # Cadena de clasificación
│   └── conversation_chain.py           # Cadena de conversación general
├── functions/
│   ├── rag_chain.py                    # Consulta documentos de pólizas (RAG)
│   ├── web_search_chain.py             # Búsqueda de noticias en la web
│   └── policy_optimizer_chain.py       # Sugerencias de optimización de pólizas
├── handlers/
│   ├── router.py                       # Clasifica y enruta al chain correcto
│   └── handle_user_query.py            # Punto de entrada para consultas de usuario
├── vector_db/
│   ├── chroma_db/                      # Base de datos ChromaDB con embeddings
│   └── documentos/                     # PDFs de pólizas de seguros
├── requirements.txt                    # Dependencias del proyecto
└── .env.example                        # Variables de entorno requeridas
```

## Requisitos previos

- **Python 3.9+**
- **API Key de OpenAI**

## Instalación

1. Clonar el repositorio y crear un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Copiar el archivo de ejemplo y configurar las variables de entorno:

```bash
cp .env.example .env
```

Editar `.env` con tus valores:

```
OPENAI_API_KEY=tu_api_key_de_openai
DB_PATH=./vector_db/chroma_db
```

4. Indexar los documentos PDF en la base de datos vectorial:

```bash
python ingest.py
```

## Ejecución

```bash
chainlit run main.py
```

Se abrirá una interfaz web en http://localhost:8000 donde podrás interactuar con Seguritos.

## Cómo funciona

1. El usuario envía una consulta.
2. La **cadena de clasificación** determina la categoría: `seguro`, `web_search`, `conversacion_general` o `policy_optimizer`.
3. El **router** dirige la consulta a la función correspondiente:
   - **seguro** -> Búsqueda RAG en documentos de pólizas
   - **web_search** -> Búsqueda de noticias con DuckDuckGo
   - **conversacion_general** -> Conversación directa con el LLM
   - **policy_optimizer** -> Análisis y sugerencias de optimización de pólizas
4. Se mantiene historial de conversación por sesión.

## Consejos para mejores resultados

- **Sé específico**: *"¿Cuáles son las coberturas de un seguro de auto en Chile?"*
- **Una pregunta a la vez**: *"¿Cómo puedo reducir el costo de mi póliza?"*
- **Usa lenguaje natural**: Formula preguntas como se las harías a una persona.
