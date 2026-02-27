import chainlit as cl
from handlers.router import router


async def handle_user_query(question: str, session_id: str = None) -> str:
    if session_id is None:
        try:
            session_id = cl.user_session.get("session_id", "default_session")
        except LookupError:
            session_id = "default_session"

    return await router(question, session_id)
