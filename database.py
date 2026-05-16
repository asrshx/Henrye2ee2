import json
import os
import time

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
TASKS_FILE = os.path.join(os.path.dirname(__file__), 'tasks.json')

DEFAULT_CONFIG = {
    'MAIN': {
        'chat_id': 'YOUR_CHAT_ID',
        'name_prefix': '[HENRY-X]',
        'delay': 10,
        'cookies': 'YOUR_COOKIES',
        'messages': 'Hello\nHi\nKya haal hai'
    }
}

def get_user_config(user_id):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        return data.get(user_id, DEFAULT_CONFIG.get(user_id))
    return DEFAULT_CONFIG.get(user_id, None)

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    data = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
    data[user_id] = {
        'chat_id': chat_id,
        'name_prefix': name_prefix,
        'delay': delay,
        'cookies': cookies,
        'messages': messages
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def set_automation_running(user_id, status):
    pass

def get_all_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_task(task_id, task_data):
    tasks = get_all_tasks()
    tasks[task_id] = task_data
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def update_task(task_id, updates):
    tasks = get_all_tasks()
    if task_id in tasks:
        tasks[task_id].update(updates)
    else:
        tasks[task_id] = updates
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def delete_task(task_id):
    tasks = get_all_tasks()
    if task_id in tasks:
        del tasks[task_id]
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)
