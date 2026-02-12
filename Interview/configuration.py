from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="gpt-5-nano",
    temperature=0,
)
