import chainlit as cl
from uuid import uuid4
from handlers.handle_user_query import handle_user_query


@cl.on_chat_start
async def on_chat_start():
    session_id = str(uuid4())
    cl.user_session.set("session_id", session_id)
    await cl.Message(
        content="¡Bienvenido! Soy **Seguritos**, tu asistente de seguros para LATAM. "
                "¿En qué puedo ayudarte hoy?"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()

    try:
        session_id = cl.user_session.get("session_id", "default_session")
        response = await handle_user_query(message.content, session_id)
        msg.content = response
        await msg.update()
    except Exception as e:
        msg.content = f"Ocurrió un error: {e}"
        await msg.update()
