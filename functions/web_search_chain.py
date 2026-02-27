from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.tools import DuckDuckGoSearchResults
from config.settings import llm, get_session_history
from prompts.conversation_prompt import web_search_prompt


async def web_search_chain(question: str, session_id: str) -> str:
    search = DuckDuckGoSearchResults(backend="news")

    try:
        raw_results = await search.ainvoke(question)

        if not raw_results or raw_results.strip() == "":
            return "No se encontraron resultados de búsqueda para tu consulta."

        chain = web_search_prompt | llm | StrOutputParser()
        chain_with_history = RunnableWithMessageHistory(
            runnable=chain,
            get_session_history=get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        response = await chain_with_history.ainvoke(
            {"input": question, "context": raw_results},
            config={"configurable": {"session_id": session_id}},
        )
        return response

    except Exception as e:
        return f"Error al realizar la búsqueda web: {e}"
