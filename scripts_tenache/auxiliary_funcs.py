

import pandas as pd
import sqlite3
from datetime import timedelta


def extract_json_from_string(s):
    new_string = s.replace("False","false")
    new_string = new_string.replace("True","true")
    start = s.find('{')  # Find the first occurrence of '{'
    end = s.rfind('}')   # Find the last occurrence of '}'
    if start != -1 and end != -1:
        new_string = new_string[start:end+1]  # Extract and return the JSON substring
    else:
        start = new_string.find("[")
        end = new_string.rfind("]")
        if start != -1 and end != -1:
          new_string = new_string[start:end+1]
          new_string = new_string.replace("[","{")
          new_string = new_string.replace("]","}")
          return new_string
        else:
          return new_string  # Return None if no JSON pattern is found
    return new_string

def extract_from_database(database_path, table, wait_time):
  with sqlite3.connect (database_path) as conn:
      c = conn.cursor()
      c.execute(f'''SELECT * FROM {table} ORDER BY created_at DESC LIMIT 1''')
      message_info = c.fetchall()[0]
      user_id = message_info[1]
      # time_stamp = datetime.strptime(info[-1], '%Y-%m-%d %H:%M:%S')
      time_stamp = message_info[-1]
      query_user = f'''SELECT id, user_id, user_name, from_user, from_ai, content FROM {table} WHERE user_id=? AND created_at >= datetime('{time_stamp}', '{wait_time}') AND from_user=1 ORDER BY created_at DESC;'''
      print(query_user)
      c.execute(query_user, (user_id,))
      all_user_messages = c.fetchall()
      query_times_user = f'''SELECT created_at FROM {table} WHERE user_id=? AND created_at >= datetime('{time_stamp}', '{wait_time}') AND from_user=1 ORDER BY created_at DESC;'''
      c.execute(query_times_user, (user_id,))
      all_user_times = c.fetchall()
      query_ai = f'''SELECT id, user_id, user_name, from_user, from_ai, content FROM {table} WHERE user_id=? AND created_at >= datetime('{time_stamp}', '{wait_time}') AND from_user=0 ORDER BY created_at DESC;'''
      c.execute(query_ai, (user_id,))
      all_ai_messages = c.fetchall()
      query_times_ai = f'''SELECT created_at FROM {table} WHERE user_id=? AND created_at >= datetime('{time_stamp}', '{wait_time}') AND from_user=0 ORDER BY created_at DESC;'''
      c.execute(query_times_ai, (user_id,))
      all_ai_times = c.fetchall()
      # info = c.fetchall()[0]
      return all_user_messages, all_ai_messages, all_user_times, all_ai_times, message_info
  
def transform_to_datetime(all_user_times, all_ai_times):
    if all_user_times:
        all_user_times = pd.to_datetime([t[0] for t in all_user_times])
    else:
        all_user_times = pd.to_datetime([])
    if all_ai_times:
        all_ai_times = pd.to_datetime([t[0] for t in all_ai_times])
    return all_user_times, all_ai_times

def group_user_messages(all_user_messages, all_ai_times, all_user_times):
    all_user_messages = pd.Series(all_user_messages)
    all_user_messages_grouped = []
    next_start = 0
    for i in range(len(all_ai_times)):
        index = all_user_times - all_ai_times[i] > timedelta(days=0)
    
        messages_now = all_user_messages[next_start:][index[next_start:]]
        next_start = len(messages_now)
        for j in range(messages_now.shape[0]):
            user_messages_grouped = messages_now.iloc[j][-1]
        all_user_messages_grouped.append(user_messages_grouped)
        return all_user_messages_grouped
    

    
def complete_messages(all_user_messages_grouped, all_ai_messages, messages):
    for i in all_user_messages_grouped:
        messages.append({
            "role":"user",
            "content":all_user_messages_grouped[i]
        })
        try:
            messages.append({
                all_ai_messages
            })
        except Exception as err:
            print(err)
            return messages


