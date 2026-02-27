import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH")

if not OPENAI_API_KEY:
    raise ValueError("Falta OPENAI_API_KEY en el archivo .env")
if not DB_PATH:
    raise ValueError("Falta DB_PATH en el archivo .env")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
)

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY,
)
vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_model)

_session_histories: dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in _session_histories:
        _session_histories[session_id] = ChatMessageHistory()
    return _session_histories[session_id]
