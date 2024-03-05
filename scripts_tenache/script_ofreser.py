import llama_cpp
import os
import sys
# import FastAPI
import sqlite3
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from auxiliary_funcs import extract_json_from_string, extract_from_database, transform_to_datetime, complete_messages, group_user_messages

response_path = os.path.join("\\","Users", "tenache89", "Desktop","llama.cpp","scripts_tenache")

table = None
columnas = None
informacion = None
TELEFONO = '4212368'
CELULAR = '387528693'
WHATSAPP = 'https://wa.me/5493875286093'
WAIT_TIME = "-5 minutes"
TABLE = "messages"

model_folder = os.path.join("\\","Users", "tenache89", "Desktop","llama.cpp", "build", "bin", "Release") 

model_name = 'EVAESPANIOLBIENTurdus-trained-20-int8.gguf'
model_path = os.path.join(model_folder, model_name)
database_folder = os.path.join("\\","Users","tenache89", "Desktop","llama.cpp","scripts_tenache")
database_name = "whatsapp3.db"
database_path = os.path.join(database_folder,database_name)

model = llama_cpp.Llama(
    model_path=model_path,
    chat_format="llama-2",
    verbose=False,
    n_ctx=1024
)

all_user_messages, all_ai_messages, all_user_times, all_ai_times, messages_info = extract_from_database(database_path, TABLE, WAIT_TIME)

all_user_times, all_ai_times = transform_to_datetime(all_user_times, all_ai_times)

all_user_messages_grouped = group_user_messages(all_user_messages, all_ai_times, all_user_times)
# Tengo que cambiar esto por user_ai_user_ai  . . . . 



messages0 =[
  {
    "role": "system",
    "content": """
    Eres el asistente de la compañía O.FRE.SER - Gestión Integral de Plagas. 
    Interactuaras con un cliente que recibirá un servicio de de control de plagas. 
    Dispones de la siguiente información:
    * Domicilio:Domicilio donde se realizará el servicio, según la información de la empresa.
    * Horario_ser :Horario programado del servicio.
    * Horario_pub :Horarios de atención al público.
    * Tels: telefonos de contacto.
      
    Tu tarea es  determinar si puedes ayudarlos o no a partir de la informacion que tienes. 
    Debes determinar si puedes ayudar con la pregunta, cual de las categorias responderia la pregunta, y si se requieren preguntas adicionales
    Debes responder en format json, con las claves:
    es_pregunta?: donde el valor sera un booleano (true o false). Esto sera verdadero si el usuario no hizo una pregunta concreta. 
    puedo_ayudar: donde el valor sera un booleano: true o false. Si el valor de es_pregunta? es false, puedo_ayudar tambien debe
    informacion_requerida: null si ninguna de las categorias ayudara a responder la pregunta. De lo contrario, responde con una de las categorias.        
    Responde solo el objeto JSON, en el siguiente formato. 
    {"es_pregunta?":bool, "puedo_ayudar":bool,"informacion_requerida":str}
    """  
    }
]

messages_json = [
  {"system":"""Tu funcion es devolver un objeto JSON a partir de los datos que se te brindaran.
   El objeto JSON debe tener la siguiente estructura:
   {"es_pregunta?":bool, "puedo_ayudar":bool,"informacion_requerida":str}
   Algunos ejemplos :
   {"es_pregunta?":true,"puedo_ayudar":true,"informacion_requerida":Horarios}
   {"es_pregunta?":false,"puedo_ayudar":false,"informacion_requerida":null}
   {"es_pregunta?":true,"puedo_ayudar":false,"informacion_requerida":null}
   {"es_pregunta?":false,"puedo_ayudar":true,"informacion_requerida":null}
   {"es_pregunta?":true,"puedo_ayudar":true,"informacion_requerida":Gustos}
   Recuerda hacerlo a partir de la informacion que te brinde el usuario
   """
   },
  {
    "role":"user",
    "content":f"{'response0'}"
  }
]

messages_no_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de 'O.FRE.SER - Gestión Integral de Plagas.
    Debes responder de manera amable a un cliente. 
    Debes explicarle a la persona que no tienes la informacion requerida para ayudar a la persona. 
    Pasales la siguiente informacion de contacto
    Telefono: {TELEFONO}. 
    Celular: {CELULAR}
    Whatsapp: {WHATSAPP}
    Donde sera atendido por un empleado de la empresa. 
    Contesta en menos de 50 palabras. 
    Recuerda ser amable a toda costa. 
    Empieza con 'Soy la IA de 'O.FRE.SER - Gestión Integral de Plagas' 
    """
  }
]

messages_more_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de O.FRE.SER - Gestión Integral de Plagas.
    Debes responder de manera amable a una persona que quiere información. 
    Todavía no sabes cual es la pregunta del usuario, y tu tarea es determinarla. 
    Esta es la informacion que hay disponible: 
    * Domicilio: Domicilio donde se realizará el servicio, según la información de la empresa.
    * Horario_ser : Horario programado del servicio.
    * Horario_pub : Horarios de atención al público.
    * Tels: telefonos de contacto.
.
    Haz mas preguntas para determinar si puedes ayudar con la informacion que tienes.
    Empieza con: 'Soy la IA de O.FRE.SER - Gestión Integral de Plagas' 
    """
  }
]

# TODO: hay que cambiar todas las variables ... 
messages_info = [
  {
    "role":"system",
    "content":f"""
    Eres el asistente de O.FRE.SER - Gestión Integral de Plagas.
    Debes responder de manera amable a una persona que quiere saber de la empresa. 
    Para responder a la pregunta, tendras la siguiente informacion:
    Debes responder con la siguiente informacion. Estas respondiendo sobre
    {table}
    Informacion requerida (tienes columnas mas informacion):
    {columnas}
    {informacion}
    Contesta en menos de 50 palabras. 
    Empieza con Soy la IA de O.FRE.SER - Gestión Integral de Plagas
    """
    }
]

start = datetime.now()
messages0_ = complete_messages(all_user_messages_grouped, all_ai_messages, messages0)

# This part determines if the AI thinks it can help or not. 
# Returns a JSON Object
chat_completion0 = model.create_chat_completion(
    messages= messages0_,
    temperature=0,
    stop=["."],
    max_tokens=50, 
    response_format={"type":"json_object"}
)['choices'][0]['message']['content'].strip()
















    
