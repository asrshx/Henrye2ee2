import streamlit as st
import streamlit.components.v1 as components
import time
import threading
import uuid
import hashlib
import os
import json
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import sqlite3
from cryptography.fernet import Fernet

# ==================== DATABASE SECTION ====================

DB_PATH = Path(__file__).parent / 'users.db'
ENCRYPTION_KEY_FILE = Path(__file__).parent / '.encryption_key'
UPLOAD_DIR = Path(__file__).parent / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

# Admin Credentials
ADMIN_USERNAME = "SAHILXWD"
ADMIN_PASSWORD = "SAHILXWD"

def get_encryption_key():
    if ENCRYPTION_KEY_FILE.exists():
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        return key

ENCRYPTION_KEY = get_encryption_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            chat_id TEXT,
            name_prefix TEXT,
            delay INTEGER DEFAULT 30,
            cookie_type TEXT DEFAULT 'single',
            cookies_encrypted TEXT,
            messages TEXT,
            is_running INTEGER DEFAULT 0,
            messages_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            log_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def encrypt_cookies(cookies):
    if not cookies:
        return None
    return cipher_suite.encrypt(cookies.encode()).decode()

def decrypt_cookies(encrypted_cookies):
    if not encrypted_cookies:
        return ""
    try:
        return cipher_suite.decrypt(encrypted_cookies.encode()).decode()
    except:
        return ""

def create_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                      (username, password_hash))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists!"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def verify_user(username, password):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (ADMIN_USERNAME,))
        admin = cursor.fetchone()
        
        if not admin:
            password_hash = hash_password(ADMIN_PASSWORD)
            cursor.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
                         (ADMIN_USERNAME, password_hash, 1))
            conn.commit()
            admin_id = cursor.lastrowid
            conn.close()
            return admin_id, True
        conn.close()
        return admin[0], True
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash, is_admin FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[1] == hash_password(password):
        return user[0], bool(user[2])
    return None, False

def create_task(user_id, task_name, chat_id, name_prefix, delay, cookie_type, cookies, messages):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    encrypted_cookies = encrypt_cookies(cookies)
    cursor.execute('''
        INSERT INTO tasks (user_id, task_name, chat_id, name_prefix, delay, cookie_type, cookies_encrypted, messages, is_running)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    ''', (user_id, task_name, chat_id, name_prefix, delay, cookie_type, encrypted_cookies, messages))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_user_tasks(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, task_name, chat_id, name_prefix, delay, cookie_type, cookies_encrypted, 
               messages, is_running, messages_sent, created_at
        FROM tasks WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    
    result = []
    for task in tasks:
        result.append({
            'id': task[0],
            'task_name': task[1],
            'chat_id': task[2],
            'name_prefix': task[3],
            'delay': task[4],
            'cookie_type': task[5],
            'cookies': decrypt_cookies(task[6]),
            'messages': task[7],
            'is_running': bool(task[8]),
            'messages_sent': task[9],
            'created_at': task[10]
        })
    return result

def get_all_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.id, t.task_name, t.chat_id, t.is_running, t.messages_sent, 
               t.created_at, u.username, t.user_id
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.created_at DESC
    ''')
    tasks = cursor.fetchall()
    conn.close()
    
    result = []
    for task in tasks:
        result.append({
            'id': task[0],
            'task_name': task[1],
            'chat_id': task[2],
            'is_running': bool(task[3]),
            'messages_sent': task[4],
            'created_at': task[5],
            'username': task[6],
            'user_id': task[7]
        })
    return result

def update_task_status(task_id, is_running):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET is_running = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                  (1 if is_running else 0, task_id))
    conn.commit()
    conn.close()

def update_task_message_count(task_id, count):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET messages_sent = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                  (count, task_id))
    conn.commit()
    conn.close()

def get_task_by_id(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, task_name, chat_id, name_prefix, delay, cookie_type, 
               cookies_encrypted, messages, is_running, messages_sent
        FROM tasks WHERE id = ?
    ''', (task_id,))
    task = cursor.fetchone()
    conn.close()
    
    if task:
        return {
            'id': task[0],
            'user_id': task[1],
            'task_name': task[2],
            'chat_id': task[3],
            'name_prefix': task[4],
            'delay': task[5],
            'cookie_type': task[6],
            'cookies': decrypt_cookies(task[7]),
            'messages': task[8],
            'is_running': bool(task[9]),
            'messages_sent': task[10]
        }
    return None

def add_task_log(task_id, log_message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO task_logs (task_id, log_message) VALUES (?, ?)',
                  (task_id, log_message))
    conn.commit()
    conn.close()

def get_task_logs(task_id, limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT log_message, created_at 
        FROM task_logs 
        WHERE task_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (task_id, limit))
    logs = cursor.fetchall()
    conn.close()
    return [(log[0], log[1]) for log in logs]

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM task_logs WHERE task_id = ?', (task_id,))
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

init_db()

# ==================== AUTOMATION LOGIC (ORIGINAL) ====================

# Global dictionary to track running tasks (outside session_state)
RUNNING_TASKS = {}

class AutomationState:
    def __init__(self, task_id):
        self.task_id = task_id
        self.running = False
        self.message_count = 0
        self.message_rotation_index = 0
        self.cookie_index = 0

def log_message(msg, task_id):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    add_task_log(task_id, formatted_msg)

def setup_browser(task_id):
    log_message('Setting up Chrome browser...', task_id)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    chromium_paths = ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/chrome']
    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', task_id)
            break
    
    try:
        from selenium.webdriver.chrome.service import Service
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed successfully!', task_id)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', task_id)
        raise error

def find_message_input(driver, process_id, task_id):
    log_message(f'{process_id}: Finding message input...', task_id)
    time.sleep(10)
    
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    except Exception:
        pass
    
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        '[contenteditable="true"]'
    ]
    
    for idx, selector in enumerate(message_input_selectors):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        log_message(f'{process_id}: Found editable element!', task_id)
                        return element
                except Exception:
                    continue
        except Exception:
            continue
    
    return None

def get_next_message(messages, message_index):
    if not messages or len(messages) == 0:
        return 'Hello!', 0
    message = messages[message_index % len(messages)]
    return message, (message_index + 1) % len(messages)

def send_messages(task_id):
    driver = None
    try:
        task = get_task_by_id(task_id)
        if not task:
            return
        
        automation_state = RUNNING_TASKS.get(task_id)
        if not automation_state:
            return
        
        process_id = f'TASK-{task_id}'
        log_message(f'{process_id}: Starting automation...', task_id)
        
        driver = setup_browser(task_id)
        
        log_message(f'{process_id}: Navigating to Facebook...', task_id)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        # Parse cookies based on type
        cookies_list = []
        if task['cookie_type'] == 'single':
            cookies_list = [task['cookies']]
        else:
            cookies_list = [c.strip() for c in task['cookies'].split('\n') if c.strip()]
        
        if not cookies_list or not cookies_list[0]:
            log_message(f'{process_id}: No cookies found!', task_id)
            update_task_status(task_id, False)
            return
        
        # Add first cookie
        current_cookie = cookies_list[automation_state.cookie_index % len(cookies_list)]
        log_message(f'{process_id}: Adding cookies...', task_id)
        
        cookie_array = current_cookie.split(';')
        for cookie in cookie_array:
            cookie_trimmed = cookie.strip()
            if cookie_trimmed:
                first_equal_index = cookie_trimmed.find('=')
                if first_equal_index > 0:
                    name = cookie_trimmed[:first_equal_index].strip()
                    value = cookie_trimmed[first_equal_index + 1:].strip()
                    try:
                        driver.add_cookie({
                            'name': name,
                            'value': value,
                            'domain': '.facebook.com',
                            'path': '/'
                        })
                    except Exception:
                        pass
        
        if task['chat_id']:
            chat_id = task['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', task_id)
            driver.get(f'https://www.facebook.com/messages/e2ee/t/{chat_id}')
            time.sleep(5)
            if '/messages/e2ee' not in driver.current_url and '/e2ee/t/' not in driver.current_url:
                driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', task_id)
            driver.get('https://www.facebook.com/messages')
        
        time.sleep(15)
        
        message_input = find_message_input(driver, process_id, task_id)
        
        if not message_input:
            log_message(f'{process_id}: Message input not found!', task_id)
            automation_state.running = False
            update_task_status(task_id, False)
            return
        
        delay = int(task['delay'])
        messages_list = [msg.strip() for msg in task['messages'].split('\n') if msg.strip()]
        
        if not messages_list:
            messages_list = ['Hello!']
        
        # Infinite loop
        while automation_state.running:
            # Get message with rotation
            base_message, automation_state.message_rotation_index = get_next_message(
                messages_list, automation_state.message_rotation_index
            )
            
            if task['name_prefix']:
                message_to_send = f"{task['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            
            try:
                # For multiple cookies, rotate
                if len(cookies_list) > 1:
                    new_cookie_index = automation_state.message_count % len(cookies_list)
                    if new_cookie_index != automation_state.cookie_index:
                        automation_state.cookie_index = new_cookie_index
                        log_message(f'{process_id}: Switching to cookie #{new_cookie_index + 1}', task_id)
                        
                        driver.delete_all_cookies()
                        driver.get('https://www.facebook.com/')
                        time.sleep(5)
                        
                        current_cookie = cookies_list[automation_state.cookie_index]
                        for cookie in current_cookie.split(';'):
                            cookie = cookie.strip()
                            if cookie and '=' in cookie:
                                name, value = cookie.split('=', 1)
                                try:
                                    driver.add_cookie({
                                        'name': name.strip(),
                                        'value': value.strip(),
                                        'domain': '.facebook.com',
                                        'path': '/'
                                    })
                                except:
                                    pass
                        
                        driver.get(f'https://www.facebook.com/messages/e2ee/t/{task["chat_id"]}')
                        time.sleep(10)
                        message_input = find_message_input(driver, process_id, task_id)
                
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    
                    element.scrollIntoView({behavior: 'smooth', block: 'center'});
                    element.focus();
                    element.click();
                    
                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                        element.innerHTML = message;
                    } else {
                        element.value = message;
                    }
                    
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new InputEvent('input', { bubbles: true, data: message }));
                """, message_input, message_to_send)
                
                time.sleep(1)
                
                sent = driver.execute_script("""
                    const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                    for (let btn of sendButtons) {
                        if (btn.offsetParent !== null) {
                            btn.click();
                            return 'button_clicked';
                        }
                    }
                    return 'button_not_found';
                """)
                
                if sent == 'button_not_found':
                    driver.execute_script("""
                        const element = arguments[0];
                        element.focus();
                        const events = [
                            new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keypress', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }),
                            new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true })
                        ];
                        events.forEach(event => element.dispatchEvent(event));
                    """, message_input)
                    log_message(f'{process_id}: Sent via Enter', task_id)
                else:
                    log_message(f'{process_id}: Sent via button', task_id)
                
                automation_state.message_count += 1
                update_task_message_count(task_id, automation_state.message_count)
                
                cookie_info = f" [Cookie #{(automation_state.cookie_index % len(cookies_list)) + 1}]" if len(cookies_list) > 1 else ""
                log_message(f'{process_id}: Message #{automation_state.message_count}{cookie_info} sent. Waiting {delay}s...', task_id)
                time.sleep(delay)
                
            except Exception as e:
                log_message(f'{process_id}: Send error: {str(e)[:100]}', task_id)
                time.sleep(5)
        
        log_message(f'{process_id}: Automation stopped. Total messages: {automation_state.message_count}', task_id)
        
    except Exception as e:
        log_message(f'Fatal error: {str(e)}', task_id)
        update_task_status(task_id, False)
    finally:
        if driver:
            try:
                driver.quit()
                log_message('Browser closed', task_id)
            except:
                pass
        
        if task_id in RUNNING_TASKS:
            del RUNNING_TASKS[task_id]

def start_automation(task_id):
    if task_id in RUNNING_TASKS:
        return
    
    automation_state = AutomationState(task_id)
    automation_state.running = True
    RUNNING_TASKS[task_id] = automation_state
    
    thread = threading.Thread(target=send_messages, args=(task_id,))
    thread.daemon = True
    thread.start()

def stop_automation(task_id):
    if task_id in RUNNING_TASKS:
        RUNNING_TASKS[task_id].running = False
    update_task_status(task_id, False)

# ==================== STREAMLIT UI ====================

st.set_page_config(
    page_title="Darkstar E2EE",
    page_icon="▶",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

* {
    font-family: 'Outfit', sans-serif !important;
}

.status-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0d0b1a 100%);
    color: white;
    padding: 12px 20px;
    z-index: 9999;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
}

.stApp {
    padding-top: 60px;
    background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0d0b1a 100%);
    background-attachment: fixed;
}

.main .block-container {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 28px;
    padding: 40px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.08);
}

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 25px;
    padding: 50px 25px;
    text-align: center;
    color: white;
}

.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 700;
    padding: 1rem 2rem;
    border-radius: 14px;
    border: none;
}

.task-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    border-left: 5px solid #667eea;
}

.console-output {
    background: #1e293b;
    border-radius: 15px;
    padding: 20px;
    font-family: "Consolas", monospace;
    max-height: 400px;
    color: #10b981;
    overflow-y: auto;
}

.console-line {
    background: #0f172a;
    padding: 8px;
    border-left: 3px solid #10b981;
    border-radius: 6px;
    margin-bottom: 8px;
}

.footer {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-top: 3rem;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

def show_status_bar():
    if st.session_state.logged_in:
        tasks = get_user_tasks(st.session_state.user_id) if not st.session_state.is_admin else get_all_tasks()
        running_tasks = sum(1 for t in tasks if t['is_running'])
        total_messages = sum(t.get('messages_sent', 0) for t in tasks)
        
        st.markdown(f"""
        <div class="status-bar">
            <div><i class="fas fa-rocket"></i> Darkstar E2EE</div>
            <div><i class="fas fa-tasks"></i> {len(tasks)} Tasks</div>
            <div><i class="fas fa-play-circle"></i> {running_tasks} Running</div>
            <div><i class="fas fa-envelope"></i> {total_messages} Messages</div>
            <div><i class="fas fa-user"></i> {st.session_state.username}</div>
        </div>
        """, unsafe_allow_html=True)

def login_page():
    st.markdown("""
    <div class="main-header">
        <h1><i class="fas fa-flag"></i> Darkstar Boii Sahiil <i class="fas fa-flag"></i></h1>
        <p>END TO END (E2EE) OFFLINE CONVERSATION SYSTEM</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign-up"])
    
    with tab1:
        st.markdown("### <i class='fas fa-sign-in-alt'></i> WELCOME BACK!", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_username", placeholder="Enter username")
        password = st.text_input("Password", key="login_password", type="password", placeholder="Enter password")
        
        if st.button("LOGIN", key="login_btn", use_container_width=True):
            if username and password:
                user_result = verify_user(username, password)
                if user_result[0]:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_result[0]
                    st.session_state.username = username
                    st.session_state.is_admin = user_result[1]
                    st.success(f"Welcome back, {username.upper()}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password!")
            else:
                st.warning("Please enter both username and password")
    
    with tab2:
        st.markdown("### <i class='fas fa-user-plus'></i> CREATE ACCOUNT", unsafe_allow_html=True)
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", key="signup_password", type="password")
        confirm_password = st.text_input("Confirm Password", key="confirm_password", type="password")
        
        if st.button("CREATE ACCOUNT", key="signup_btn", use_container_width=True):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    success, message = create_user(new_username, new_password)
                    if success:
                        st.success(f"{message} Please login now!")
                    else:
                        st.error(f"{message}")
                else:
                    st.error("Passwords do not match!")
            else:
                st.warning("Please fill all fields")

def user_dashboard():
    show_status_bar()
    
    st.markdown("""
    <div class="main-header">
        <h1><i class="fas fa-flag"></i> Darkstar Boii Sahiil <i class="fas fa-flag"></i></h1>
        <p>FACEBOOK E2EE AUTOMATION</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f'<div style="text-align:center"><i class="fas fa-user-circle" style="font-size:3rem;color:#667eea"></i></div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"### <i class='fas fa-user'></i> {st.session_state.username}", unsafe_allow_html=True)
    
    if st.sidebar.button("LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.is_admin = False
        st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["Create Task", "My Tasks", "Console"])
    
    with tab1:
        st.markdown("### <i class='fas fa-plus-circle'></i> CREATE NEW TASK", unsafe_allow_html=True)
        
        task_name = st.text_input("Task Name", placeholder="e.g., Birthday Messages")
        chat_id = st.text_input("Chat ID (E2EE)", placeholder="e.g., 10000634210631")
        name_prefix = st.text_input("Name Prefix (Optional)", placeholder="e.g., Happy Birthday")
        delay = st.number_input("Delay (seconds)", min_value=1, max_value=300, value=30)
        
        cookie_type = st.radio("Cookie Type", ["single", "multiple"], horizontal=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if cookie_type == "single":
                cookies_input = st.text_area("Single Cookie", placeholder="Paste cookie here", height=150)
            else:
                cookies_file = st.file_uploader("Upload Cookies File (.txt)", type=['txt'], key="cookies_file")
                cookies_input = ""
                if cookies_file:
                    cookies_input = cookies_file.read().decode('utf-8')
                    st.success(f"Loaded {len([c for c in cookies_input.split('\n') if c.strip()])} cookies")
        
        with col2:
            messages_file = st.file_uploader("Upload Messages File (.txt)", type=['txt'], key="messages_file")
            if messages_file:
                messages_input = messages_file.read().decode('utf-8')
                st.success(f"Loaded {len([m for m in messages_input.split('\n') if m.strip()])} messages")
            else:
                messages_input = st.text_area("Messages (one per line)", placeholder="Enter messages", height=150)
        
        if st.button("CREATE & START TASK", use_container_width=True):
            if task_name and chat_id and cookies_input and messages_input:
                task_id = create_task(
                    st.session_state.user_id,
                    task_name,
                    chat_id,
                    name_prefix,
                    delay,
                    cookie_type,
                    cookies_input,
                    messages_input
                )
                start_automation(task_id)
                st.success(f"Task '{task_name}' created and started!")
                st.rerun()
            else:
                st.error("Please fill all required fields!")
    
    with tab2:
        st.markdown("### <i class='fas fa-list'></i> MY TASKS", unsafe_allow_html=True)
        
        tasks = get_user_tasks(st.session_state.user_id)
        
        if not tasks:
            st.info("No tasks yet. Create your first task!")
        else:
            for task in tasks:
                st.markdown(f"""
                <div class="task-card">
                    <h3><i class="fas fa-tasks"></i> {task['task_name']}</h3>
                    <p><i class="fas fa-comment"></i> Chat: {task['chat_id'][:15]}...</p>
                    <p><i class="fas fa-envelope"></i> Messages: {task['messages_sent']} | 
                       <i class="fas fa-clock"></i> Delay: {task['delay']}s | 
                       Status: {'<span style="color:#10b981">RUNNING</span>' if task['is_running'] else '<span style="color:#ef4444">STOPPED</span>'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    if not task['is_running']:
                        if st.button(f"<i class='fas fa-play'></i> Start", key=f"start_{task['id']}", use_container_width=True):
                            update_task_status(task['id'], True)
                            start_automation(task['id'])
                            st.success("Task started!")
                            st.rerun()
                    else:
                        if st.button(f"<i class='fas fa-stop'></i> Stop", key=f"stop_{task['id']}", use_container_width=True):
                            stop_automation(task['id'])
                            st.warning("Task stopped!")
                            st.rerun()
                
                with col2:
                    if st.button(f"<i class='fas fa-terminal'></i> Logs", key=f"logs_{task['id']}", use_container_width=True):
                        st.session_state[f'show_logs_{task["id"]}'] = not st.session_state.get(f'show_logs_{task["id"]}', False)
                        st.rerun()
                
                with col3:
                    if st.button(f"<i class='fas fa-trash'></i> Delete", key=f"delete_{task['id']}", use_container_width=True):
                        if task['is_running']:
                            stop_automation(task['id'])
                        delete_task(task['id'])
                        st.success("Task deleted!")
                        st.rerun()
                
                if st.session_state.get(f'show_logs_{task["id"]}', False):
                    logs = get_task_logs(task['id'], limit=30)
                    if logs:
                        logs_html = '<div class="console-output">'
                        for log, timestamp in reversed(logs):
                            logs_html += f'<div class="console-line">{log}</div>'
                        logs_html += '</div>'
                        st.markdown(logs_html, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### <i class='fas fa-terminal'></i> CONSOLE", unsafe_allow_html=True)
        
        tasks = get_user_tasks(st.session_state.user_id)
        
        if tasks:
            task_names = [f"{t['task_name']} (ID: {t['id']})" for t in tasks]
            selected_task_index = st.selectbox("Select Task", range(len(tasks)), format_func=lambda i: task_names[i])
            
            if selected_task_index is not None:
                selected_task = tasks[selected_task_index]
                logs = get_task_logs(selected_task['id'], limit=50)
                
                if logs:
                    logs_html = '<div class="console-output">'
                    for log, timestamp in reversed(logs):
                        logs_html += f'<div class="console-line">{log}</div>'
                    logs_html += '</div>'
                    st.markdown(logs_html, unsafe_allow_html=True)
                    
                    if st.button("Refresh Logs", use_container_width=True):
                        st.rerun()
                else:
                    st.info("No logs yet")
        else:
            st.info("No tasks available")

def admin_dashboard():
    show_status_bar()
    
    st.markdown("""
    <div class="main-header">
        <h1><i class="fas fa-crown"></i> ADMIN DASHBOARD <i class="fas fa-crown"></i></h1>
        <p>FULL SYSTEM CONTROL</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f'<div style="text-align:center"><i class="fas fa-user-shield" style="font-size:3rem;color:#667eea"></i></div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"### <i class='fas fa-crown'></i> ADMIN: {st.session_state.username}", unsafe_allow_html=True)
    
    if st.sidebar.button("LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.is_admin = False
        st.rerun()
    
    st.markdown("### <i class='fas fa-globe'></i> ALL USERS TASKS", unsafe_allow_html=True)
    
    all_tasks = get_all_tasks()
    
    if not all_tasks:
        st.info("No tasks in system")
    else:
        for task in all_tasks:
            st.markdown(f"""
            <div class="task-card">
                <h3><i class="fas fa-tasks"></i> {task['task_name']}</h3>
                <p><i class="fas fa-user"></i> User: {task['username']} | 
                   <i class="fas fa-comment"></i> Chat: {task['chat_id'][:15]}... | 
                   <i class="fas fa-envelope"></i> Messages: {task['messages_sent']}</p>
                <p>Status: {'<span style="color:#10b981">RUNNING</span>' if task['is_running'] else '<span style="color:#ef4444">STOPPED</span>'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if task['is_running']:
                    if st.button(f"<i class='fas fa-stop'></i> STOP", key=f"admin_stop_{task['id']}", use_container_width=True):
                        stop_automation(task['id'])
                        st.warning("Task stopped by admin!")
                        st.rerun()
            
            with col2:
                if st.button(f"<i class='fas fa-trash'></i> DELETE", key=f"admin_delete_{task['id']}", use_container_width=True):
                    if task['is_running']:
                        stop_automation(task['id'])
                    delete_task(task['id'])
                    st.success("Task deleted by admin!")
                    st.rerun()

def show_footer():
    st.markdown("""
    <div class="footer">
        <p><i class="fas fa-code"></i> Developer: Darkstar Boii Sahiil</p>
        <p><i class="fas fa-users"></i> Team: Darkstar</p>
        <p>Made in India 2026</p>
        <p><a href="#" style="color:white"><i class="fas fa-file-contract"></i> Terms of Condition</a></p>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.is_admin:
        admin_dashboard()
    else:
        user_dashboard()

show_footer()
