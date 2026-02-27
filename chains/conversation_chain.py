from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from config.settings import llm, get_session_history
from prompts.conversation_prompt import conversation_prompt

_base_chain = conversation_prompt | llm | StrOutputParser()

conversation_chain = RunnableWithMessageHistory(
    runnable=_base_chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)
