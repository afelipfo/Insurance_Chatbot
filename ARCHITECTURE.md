# Arquitectura del Chatbot con Clasificación y RAG

## Visión general

Sistema conversacional basado en LLM que clasifica automáticamente las consultas del usuario y las enruta a cadenas especializadas. Combina Retrieval-Augmented Generation (RAG) sobre documentos propios, búsqueda web en tiempo real, análisis/optimización de documentos y conversación general, todo con historial de sesión persistente.

```
Usuario
  │
  ▼
┌──────────────────┐
│   UI (Chainlit)  │  main.py
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Handler de      │  handlers/handle_user_query.py
│  consulta        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     Router       │  handlers/router.py
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Clasificador    │  chains/classification_chain.py
│  (LLM + Prompt)  │
└────────┬─────────┘
         │
    ┌────┼─────────┬──────────────┐
    ▼    ▼         ▼              ▼
┌──────┐┌────────┐┌────────────┐┌──────────────┐
│ RAG  ││  Web   ││ Optimizador││ Conversación │
│Chain ││Search  ││ de docs    ││   General    │
└──────┘└────────┘└────────────┘└──────────────┘
```

---

## Estructura de directorios

```
proyecto/
├── config/
│   └── settings.py            # LLM, embeddings, vector DB, historial de sesión
├── prompts/
│   ├── classification_prompt.py   # Prompt de clasificación de intención
│   └── conversation_prompt.py     # Prompts por cada cadena especializada
├── chains/
│   ├── classification_chain.py    # Cadena LCEL: prompt → LLM → parser
│   └── conversation_chain.py      # Cadena de conversación general con historial
├── functions/
│   ├── rag_chain.py               # RAG: retriever + LLM con historial
│   ├── web_search_chain.py        # Búsqueda web + LLM con historial
│   └── policy_optimizer_chain.py  # Análisis de documentos + LLM con historial
├── handlers/
│   ├── handle_user_query.py       # Punto de entrada para cada consulta
│   └── router.py                  # Clasificación → despacho a cadena correcta
├── vector_db/
│   ├── chroma_db/                 # Base de datos vectorial persistida
│   └── documentos/                # Documentos fuente (PDFs)
├── main.py                        # Punto de entrada de la aplicación (Chainlit)
├── ingest.py                      # Script de ingesta de documentos a ChromaDB
├── .env                           # Variables de entorno (API keys, rutas)
└── requirements.txt
```

---

## Componentes

### 1. Configuración centralizada (`config/settings.py`)

Punto único de configuración. Inicializa y exporta:

| Objeto | Tipo | Propósito |
|---|---|---|
| `llm` | `ChatOpenAI` | Modelo de lenguaje (gpt-4o-mini) |
| `embedding_model` | `OpenAIEmbeddings` | Modelo de embeddings (text-embedding-3-small) |
| `vector_db` | `Chroma` | Conexión a la base de datos vectorial |
| `get_session_history(session_id)` | Función | Retorna `ChatMessageHistory` por sesión |

El historial se almacena en un diccionario en memoria (`dict[str, ChatMessageHistory]`), lo que permite mantener conversaciones independientes por sesión sin estado compartido entre usuarios.

### 2. Sistema de prompts (`prompts/`)

**`classification_prompt.py`** — Prompt de clasificación de intención mediante `ChatPromptTemplate.from_messages`. El LLM recibe instrucciones de sistema con las categorías válidas y responde exclusivamente con el nombre de la categoría.

**`conversation_prompt.py`** — Define un `SYSTEM_PROMPT` base compartido y cuatro variantes de prompt:

| Prompt | Variables de entrada | Uso |
|---|---|---|
| `conversation_prompt` | `history`, `input` | Conversación general |
| `rag_prompt` | `history`, `input`, `context` | Respuesta basada en documentos |
| `web_search_prompt` | `history`, `input`, `context` | Resumen de resultados web |
| `policy_optimizer_prompt` | `history`, `input`, `context` | Análisis y optimización de documentos |

Todos incluyen `MessagesPlaceholder(variable_name="history")` para inyectar el historial conversacional.

### 3. Cadenas LCEL (`chains/`)

**`classification_chain.py`** — Cadena mínima con LangChain Expression Language:

```
classification_prompt | llm | StrOutputParser()
```

Recibe `{"question": str}`, retorna la categoría como string.

**`conversation_chain.py`** — Cadena con historial:

```
conversation_prompt | llm | StrOutputParser()
```

Envuelta en `RunnableWithMessageHistory` para gestión automática del historial por `session_id`.

### 4. Funciones especializadas (`functions/`)

Cada función sigue el mismo patrón:

1. **Obtener contexto**: retriever desde ChromaDB o búsqueda web.
2. **Construir cadena**: `prompt | llm | StrOutputParser()`.
3. **Envolver con historial**: `RunnableWithMessageHistory`.
4. **Invocar asincrónicamente**: pasando `input`, `context` y `session_id`.
5. **Manejar errores**: try/except con mensajes descriptivos.

| Función | Fuente de contexto | Prompt |
|---|---|---|
| `rag_chain` | `vector_db.as_retriever(k=5)` | `rag_prompt` |
| `web_search_chain` | `DuckDuckGoSearchResults(backend="news")` | `web_search_prompt` |
| `policy_optimizer_chain` | `vector_db.as_retriever(k=5)` | `policy_optimizer_prompt` |

### 5. Router (`handlers/router.py`)

Orquesta el flujo completo:

1. Invoca `classification_chain` con la consulta del usuario.
2. Normaliza la respuesta (minúsculas, sin acentos).
3. Valida contra el set de categorías permitidas.
4. Despacha a la cadena correspondiente.
5. En caso de categoría no reconocida, cae a conversación general.

### 6. Handler de consulta (`handlers/handle_user_query.py`)

Capa delgada entre la UI y el router. Resuelve el `session_id` (desde Chainlit o un valor por defecto) y delega al router.

### 7. Ingesta de documentos (`ingest.py`)

Script independiente que:

1. Escanea el directorio de documentos buscando PDFs.
2. Carga cada PDF con `PyPDFLoader`.
3. Divide en chunks con `RecursiveCharacterTextSplitter` (1000 caracteres, 200 de overlap).
4. Genera embeddings con OpenAI.
5. Persiste en ChromaDB.
6. Ejecuta una búsqueda de verificación al finalizar.

### 8. Punto de entrada (`main.py`)

Aplicación Chainlit con dos hooks:

- **`on_chat_start`**: genera `session_id` único (UUID), lo almacena en la sesión de Chainlit y envía mensaje de bienvenida.
- **`on_message`**: envía un mensaje vacío (para mostrar indicador de carga), procesa la consulta vía `handle_user_query` y actualiza el mensaje con la respuesta.

---

## Flujo de datos

```
1. Usuario envía mensaje
       │
2. main.py → handle_user_query(mensaje, session_id)
       │
3. router → classification_chain.ainvoke({"question": mensaje})
       │
4. LLM clasifica → "rag" | "web_search" | "optimizer" | "conversacion_general"
       │
5. Router despacha a la cadena correspondiente
       │
       ├─ RAG: retriever.ainvoke(pregunta) → docs → rag_prompt + LLM
       ├─ Web: DuckDuckGoSearch.ainvoke(pregunta) → resultados → web_prompt + LLM
       ├─ Optimizer: retriever.ainvoke(pregunta) → docs → optimizer_prompt + LLM
       └─ General: conversation_prompt + LLM
       │
6. Respuesta con historial de sesión → usuario
```

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| UI | Chainlit |
| Orquestación LLM | LangChain (LCEL) |
| Modelo de lenguaje | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Base vectorial | ChromaDB |
| Búsqueda web | DuckDuckGo Search |
| Carga de documentos | PyPDFLoader |
| Gestión de historial | RunnableWithMessageHistory + ChatMessageHistory |
| Variables de entorno | python-dotenv |

---

## Cómo adaptar a otro dominio

1. **Prompts**: modificar `SYSTEM_PROMPT` en `conversation_prompt.py` con la personalidad y dominio del asistente. Ajustar los prompts específicos de cada cadena.
2. **Categorías**: actualizar las categorías en `classification_prompt.py` y el set `VALID_CATEGORIES` en `router.py`.
3. **Documentos**: reemplazar los PDFs en `vector_db/documentos/` y ejecutar `python ingest.py`.
4. **Cadenas**: agregar o eliminar funciones en `functions/` según las capacidades requeridas, y registrar las nuevas rutas en el router.
5. **Configuración**: ajustar modelo, embeddings o base vectorial en `config/settings.py`.

---

## Variables de entorno

```env
OPENAI_API_KEY=sk-...
DB_PATH=./vector_db/chroma_db
```

---

## Ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar .env con las variables requeridas

# 3. Ingestar documentos en la base vectorial
python ingest.py

# 4. Iniciar la aplicación
chainlit run main.py -w --port 8000
```
