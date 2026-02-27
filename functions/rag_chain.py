from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from config.settings import llm, vector_db, get_session_history
from prompts.conversation_prompt import rag_prompt


async def rag_chain(question: str, session_id: str) -> str:
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    try:
        retrieved_docs = await retriever.ainvoke(question)

        if not retrieved_docs:
            return "Lo siento, no se encontraron documentos relevantes para tu consulta."

        context = "\n\n".join(doc.page_content for doc in retrieved_docs)

        chain = rag_prompt | llm | StrOutputParser()
        chain_with_history = RunnableWithMessageHistory(
            runnable=chain,
            get_session_history=get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        response = await chain_with_history.ainvoke(
            {"input": question, "context": context},
            config={"configurable": {"session_id": session_id}},
        )
        return response

    except Exception as e:
        return f"Error al consultar documentos: {e}"
