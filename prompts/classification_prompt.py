from langchain_core.prompts import ChatPromptTemplate

classification_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Clasifica la consulta del usuario en exactamente una de estas categorías:\n"
        "- seguro\n"
        "- web_search\n"
        "- conversacion_general\n"
        "- policy_optimizer\n\n"
        "Responde ÚNICAMENTE con el nombre de la categoría, sin explicación."
    )),
    ("human", "{question}"),
])
