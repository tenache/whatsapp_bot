#!/usr/bin/env python
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.output_parsers import StrOutputParser
from fastapi import FastAPI
from langserve import add_routes
import os

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's piRunnable interfaces",
)
# C:\Users\tenache89\Desktop\llama.cpp\build\bin\Release
model_folder = os.path.join("\\","Users", "tenache89", "Desktop", "llama.cpp", "build","bin", "Release") 
model_name = 'llama-2-13b-chat.Q5_K_M.gguf'
model_path = os.path.join(model_folder, model_name)

model = LlamaCpp(
    model_path=model_path,
    temperature=0,
    max_tokens=200,
    top_p=1,
    #callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
    stop=["Human:"],
)

prompt = ChatPromptTemplate.from_messages([
            ("system", """"You are an assistant who's main role is to answer simple questions. 
             If you don't know the answer, you must redirect them to the number: 3875377223"!'"""),
            ("human","Hello, at what time do you open?"),
            ("ai","I'm sorry, I don't know the answer to your question. Please contact the number: 3875377223, where you will be attended by an employee. "),
            ("human","{user_input}"),
            ("ai",""),

        ])

# prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")

add_routes(
    app,
    prompt | model,
    path="/joke",
)

@app.get("/")
def read_root():
    return {"Hello":"World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)