import llama_cpp
import os
import sys
# import FastAPI
import sqlite3
import json
from datetime import datetime
import numpy as np
import pandas as pd

table = None
columnas = None
informacion = None
TELEFONO = '3875377223'
WAIT_TIME = "-5 hours"
# app = FastAPI(
#     title="Chatbot server",
#     version="1.0",
#     description="A simple api server using llama's piRunnable interfaces",
# )

model_folder = os.path.join("\\","Users", "tenache89", "Desktop","llama.cpp", "build", "bin", "Release") 
# model_name = 'llama-2-13b-chat.Q5_K_M.gguf'
model_name = 'EVAESPANIOLBIENTurdus-trained-20-int8.gguf'
model_path = os.path.join(model_folder, model_name)
database_folder = os.path.join("\\","Users","tenache89", "Desktop","llama.cpp","build","bin","Release","scripts")
database_name = "whatsapp2.db"
database_path = os.path.join(database_folder,database_name)


model = llama_cpp.Llama(
    model_path=model_path,
    chat_format="llama-2",
    verbose=False
)

print(f"database_path is {database_path}")
with sqlite3.connect (database_path) as conn:
    c = conn.cursor()
    c.execute('''SELECT * FROM messages ORDER BY created_at DESC LIMIT 1''')
    info = c.fetchall()[0]
    user_id = info[1]
    time_stamp = datetime.strptime(info[-1], '%Y-%m-%d %H:%M:%S')
    c.execute(f'''SELECT id, user_id, user_name, from_user, from_ai, content FROM messages WHERE user_id=? AND created_at >= datetime({time_stamp}, '{WAIT_TIME}') AND from_user=1 ORDER BY created_at DESC;''', (user_id,))
    all_user_messages = c.fetchall()
    c.execute(f'''SELECT created_at FROM messages WHERE user_id=? AND created_at >= datetime({time_stamp}, '{WAIT_TIME}') AND from_user=1 ORDER BY created_at DESC;''', (user_id,))
    all_user_times = c.fetchall()
    c.execute(f'''SELECT id, user_id, user_name, from_user, from_ai, content FROM messages WHERE user_id=? AND created_at >= datetime({time_stamp}, '{WAIT_TIME}') AND from_user=0 ORDER BY created_at DESC;''', (user_id,))
    all_ai_messages = c.fetchall()
    c.execute(f'''SELECT created_at FROM messages WHERE user_id=? AND created_at >= datetime({time_stamp}, '{WAIT_TIME}') AND from_user=0 ORDER BY created_at DESC;''', (user_id,))
    all_ai_times = c.fetchall()
    # info = c.fetchall()[0]

all_user_times = all_ai_times = pd.to_datetime(all_user_times)
all_ai_times = pd.to_datetime(all_ai_times)

all_user_messages_grouped = ""
next_start = 0

if len(all_ai_times):
  sections = len(all_ai_times)
else:
  sections = 1
  
for i in range(len(all_ai_times)):
  all_user_messages_grouped += "\n"
  messages_now = all_user_messages[next_start:][all_user_times - all_ai_times[i] > 0]
  next_start = len(messages_now)
  for j in messages_now:
    all_user_messages_grouped[i] += messages_now[j]
    
for message in all_user_messages:
  all_user_messages_grouped += message
  
    



  



print(f"info is {info}")
print(f"type(info) is {type(info)}")

print()
content = info[5]
pregunta = "Hola"

messages0 =[
  {
    "role": "system",
    "content": """
    Eres el asistente de Thomas. Tu tarea es interactuar con personas y determinar si puedes ayudarlos o no a partir de la informacion que tienes
    Dispones de las siguientes categorias de informacion: {Amigos, Gustos, Hobbies, Horarios, LibrosFavoritos, PeliculasFavoritas}. 
    Debes determinar si puedes ayudar con la pregunta, cual de las categorias responderia la pregunta, y si se requieren preguntas adicionales
    Debes responder en format json, con las claves:
    es_pregunta?: donde el valor sera un booleano (true o false). Esto sera verdadero si el usuario no hizo una pregunta concreta. 
    
    puedo_ayudar: donde el valor sera un booleano: true o false
    informacion_requerida: donde debes responder con una de las categorias de informacion dadas anteriormente. o null si no puedes contestar.      
    Responde solo el objeto JSON, en el siguiente formato. 
    {"es_pregunta?":bool, "puedo_ayudar":str,"informacion_requerida":str}
    """  
    },
  {
    "role":"user",
    "content":pregunta
  }
]

start = datetime.now()
chat_completion0 = model.create_chat_completion(
    messages= messages0,
    temperature=0,
    stop=["."],
    max_tokens=50, 
    response_format={"type":"json_object"}
)

print(f"La LLM tomo {datetime.now() - start}")
response0 = chat_completion0['choices'][0]['message']['content'].strip()

try:
  json_dict = json.loads(response0)
except Exception as err:
  print(err)
  print(f"response0 is {response0}")
  
table = json_dict['informacion_requerida']
  
info_data_name = 'info.db'
info_data_path = os.path.join(database_folder, info_data_name)
if table: 
  with sqlite3.connect(info_data_path) as conn:
    c = conn.cursor()
    c.execute(f'''SELECT * FROM {table}''')
    all_info = c.fetchall()
    column_names = [description[0] for description in c.description]
    info = all_info[0]

  columnas = column_names[0]
  for column in column_names[1:]:
    columnas += "," + column
  informacion = str(all_info[0])

  for info in all_info[1:]:
    informacion += "\n" + str(info)


messages_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de Thomas. Debes responder de manera amable a una persona que quiere saber de Thomas. 
    Para responder a la pregunta, tendras la siguiente informacion:
    Debes responder con la siguiente informacion. Estas respondiendo sobre
    {table}
    Informacion requerida (tienes columnas mas informacion):
    {columnas}
    {informacion}
    Contesta en menos de 35 palabras. 
    Empieza con: 'Soy la IA de Thomas'
    """
  },
  {
    "role":"user",
    "content": pregunta
  }
]

messages_no_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de Thomas. Debes responder de manera amable a una persona que quiere saber de Thomas. 
    Debes explicarle a la persona que no tienes la informacion requerida para ayudar a la persona. 
    Diles que se comuniquen al numero: {TELEFONO}. 
    Contesta en menos de 40 palabras. 
    Recuerda ser amable a toda costa. 
    Empieza con 'Soy la IA de Thomas' 
    """
  },
  {
    "role":"user",
    "content": pregunta
  }
]

messages_more_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de Thomas. Debes responder de manera amable a una persona que quiere saber de Thomas. 
    Todavia no sabes si puedes brindar la informacion necesaria. Esta es la informacion que posees: 
    {{Amigos, Gustos, Hobbies, Horarios, LibrosFavoritos, PeliculasFavoritas}}
    Haz mas preguntas para determinar si puedes ayudar con la informacion que tienes.
    Empieza con: 'Soy la IA de Thomas' 
    """
  },
  {
    "role":"user",
    "content": pregunta
  }
]
  
print("The second completion is underway . . .")

start = datetime.now()

if table: 
  chat_completion = model.create_chat_completion(
    messages = messages_info,
    temperature = 0,
    max_tokens=5000
  )
elif not json_dict['es_pregunta?']:
    chat_completion = model.create_chat_completion(
    messages = messages_more_info,
    temperature=0.25,
    max_tokens=5000
  )
  
else:
  chat_completion = model.create_chat_completion(
    messages = messages_no_info,
    temperature=0.25,
    max_tokens=5000
  )
  

print(f"La segunda LLM tomo {datetime.now()-start}")

response = chat_completion['choices'][0]['message']['content'].strip()
print(f"response is {response}")





#info.id, info.user_id, 0, 1, response,


# DO NOT ELIMINATE FOLLOWING LINES!!!!!!
# message_id = info[0] + "_ai"
# print(f"response is {response}")
# values = (message_id,info[1],info[2],0,1,response)
# with sqlite3.connect(database_path) as conn:
#     c = conn.cursor()
#     c.execute(f'''INSERT INTO messages (id, user_id, user_name, from_user, from_ai, content) VALUES (?, ?, ?, ?, ?, ?);''', values)

response_path = r'C:\Users\tenache89\Desktop\llama.cpp\build\bin\Release\scripts\mensaje.txt'
with open(response_path,'w') as file:
    file.write(response)


# print(model("The quick brown fox jumps ", stop=["."])["choices"][0]["text"])
