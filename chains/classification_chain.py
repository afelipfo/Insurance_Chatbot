from langchain_core.output_parsers import StrOutputParser
from config.settings import llm
from prompts.classification_prompt import classification_prompt

classification_chain = classification_prompt | llm | StrOutputParser()
