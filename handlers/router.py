from chains.classification_chain import classification_chain
from chains.conversation_chain import conversation_chain
from functions.rag_chain import rag_chain
from functions.web_search_chain import web_search_chain
from functions.policy_optimizer_chain import policy_optimizer_chain

VALID_CATEGORIES = {"seguro", "web_search", "conversacion_general", "policy_optimizer"}


async def router(question: str, session_id: str) -> str:
    try:
        raw_category = await classification_chain.ainvoke({"question": question})
        category = raw_category.strip().lower().replace("á", "a").replace("é", "e").replace("ó", "o")

        if category not in VALID_CATEGORIES:
            category = "conversacion_general"

        if category == "seguro":
            return await rag_chain(question, session_id)

        if category == "web_search":
            return await web_search_chain(question, session_id)

        if category == "policy_optimizer":
            return await policy_optimizer_chain(question, session_id)

        return await conversation_chain.ainvoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}},
        )

    except Exception as e:
        return f"Error al procesar tu consulta: {e}"
