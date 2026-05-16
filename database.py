# database.py - HENRY-X Database System
# Multi-Task + Multi-User Support
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

# ════════════════════════════════════════════════
# USER CONFIG (Same as before)
# ════════════════════════════════════════════════

def get_user_config(user_id):
    """Get user configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            data = json.load(f)
        return data.get(user_id, DEFAULT_CONFIG.get(user_id))
    return DEFAULT_CONFIG.get(user_id, None)

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    """Save/update user configuration"""
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
    pass  # Backward compatibility


# ════════════════════════════════════════════════
# MULTI-TASK SYSTEM (NEW - UPGRADED)
# ════════════════════════════════════════════════

def get_all_tasks():
    """Get all saved tasks from persistent storage.
    Returns dict: {task_id: {name, status, config, msg_count, created_at, ...}}
    """
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_task(task_id, task_data):
    """Save a new task to persistent storage.
    
    Args:
        task_id: Unique task identifier (string)
        task_data: Dict with task info (name, status, config, msg_count, etc.)
    """
    tasks = get_all_tasks()
    tasks[task_id] = task_data
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def update_task(task_id, updates):
    """Update specific fields of an existing task.
    
    Args:
        task_id: Task to update
        updates: Dict of fields to update/merge
    """
    tasks = get_all_tasks()
    if task_id in tasks:
        tasks[task_id].update(updates)
    else:
        # If task doesn't exist, create it with updates
        tasks[task_id] = updates
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def delete_task(task_id):
    """Delete a task from storage.
    
    Args:
        task_id: Task to remove
    """
    tasks = get_all_tasks()
    if task_id in tasks:
        del tasks[task_id]
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)

def get_task(task_id):
    """Get a single task by ID.
    
    Returns: Dict or None if not found
    """
    tasks = get_all_tasks()
    return tasks.get(task_id, None)

def get_running_tasks():
    """Get all currently running tasks.
    
    Returns: Dict of {task_id: task_data}
    """
    tasks = get_all_tasks()
    return {tid: t for tid, t in tasks.items() if t.get('status') == 'running'}

def get_tasks_by_status(status):
    """Get tasks filtered by status (running, paused, completed, stopped, error).
    
    Returns: Dict of {task_id: task_data}
    """
    tasks = get_all_tasks()
    return {tid: t for tid, t in tasks.items() if t.get('status') == status}

def cleanup_old_tasks(hours=24):
    """Remove or archive tasks older than specified hours.
    Returns number of tasks affected.
    """
    tasks = get_all_tasks()
    now = time.time()
    cutoff = now - (hours * 3600)
    affected = 0
    
    for task_id in list(tasks.keys()):
        task = tasks[task_id]
        completed = task.get('completed_at', 0)
        created = task.get('created_at', 0)
        
        # Only cleanup completed/stopped/error tasks
        if task.get('status') in ['completed', 'stopped', 'error']:
            if completed and completed < cutoff:
                # Don't delete, just mark as archived
                tasks[task_id]['archived'] = True
                tasks[task_id]['logs_summary'] = f"Archived after {hours}h | Msgs: {task.get('msg_count', 0)}"
                # Clear heavy logs
                if 'logs' in tasks[task_id]:
                    del tasks[task_id]['logs']
                affected += 1
    
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)
    
    return affected

def get_task_stats():
    """Get overall task statistics.
    Returns dict with counts by status.
    """
    tasks = get_all_tasks()
    stats = {
        'total': len(tasks),
        'running': 0,
        'paused': 0,
        'completed': 0,
        'stopped': 0,
        'error': 0,
        'total_messages': 0
    }
    
    for task in tasks.values():
        status = task.get('status', 'unknown')
        if status in stats:
            stats[status] += 1
        else:
            stats[status] = 1
        stats['total_messages'] += task.get('msg_count', 0)
    
    return stats
