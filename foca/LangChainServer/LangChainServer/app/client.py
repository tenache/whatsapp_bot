from langchain.prompts.chat import ChatPromptTemplate
from langserve import RemoteRunnable

a = RemoteRunnable("http://localhost:8000/joke")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a highly educated person who loves to use big words. "
            + "You are also concise. Never answer in more than three sentences.",
        ),
        ("human", "Tell me about your favorite novel"),
    ]
).format_messages() 

# a.invoke(prompt)

