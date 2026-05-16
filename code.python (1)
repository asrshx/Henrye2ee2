import streamlit as st
import streamlit.components.v1 as components
import time
import threading
import uuid
import hashlib
import os
import json
import urllib.parse
import queue
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests
import re

st.set_page_config(
    page_title="HENRY-X • NextGen Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PINK + PURPLE GRADIENT ULTRA COOL THEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    /* MAIN BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #ff1493 0%, #8a2be2 50%, #4a0080 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* MAIN BLOCK CONTAINER */
    .main > div {
        background: rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin: 10px 0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* HEADER STYLE */
    .henryx-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, rgba(255,20,147,0.3), rgba(138,43,226,0.3));
        border-radius: 20px;
        border: 2px solid rgba(255,255,255,0.2);
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    
    .henryx-title {
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(90deg, #ff69b4, #da70d6, #9370db, #ff69b4);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s ease-in-out infinite;
        text-shadow: none;
        letter-spacing: 5px;
    }
    
    @keyframes shimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .henryx-subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 16px;
        margin-top: 5px;
        font-weight: 300;
        letter-spacing: 2px;
    }
    
    /* TASK CARDS */
    .task-card {
        background: linear-gradient(135deg, rgba(255,20,147,0.15), rgba(138,43,226,0.15));
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 16px;
        padding: 18px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .task-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transition: 0.5s;
    }
    
    .task-card:hover::before {
        left: 100%;
    }
    
    .task-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(138,43,226,0.3);
        border-color: rgba(255,255,255,0.3);
    }
    
    .task-name {
        font-size: 18px;
        font-weight: 700;
        color: #fff;
        margin-bottom: 8px;
    }
    
    .task-meta {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        margin: 8px 0;
    }
    
    .task-badge {
        background: rgba(255,255,255,0.1);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        color: rgba(255,255,255,0.8);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .task-badge.running {
        background: rgba(0,255,100,0.2);
        border-color: rgba(0,255,100,0.3);
        color: #00ff64;
    }
    
    .task-badge.paused {
        background: rgba(255,165,0,0.2);
        border-color: rgba(255,165,0,0.3);
        color: #ffa500;
    }
    
    .task-badge.completed {
        background: rgba(100,149,237,0.2);
        border-color: rgba(100,149,237,0.3);
        color: #6495ed;
    }
    
    .task-badge.stopped {
        background: rgba(255,0,0,0.2);
        border-color: rgba(255,0,0,0.3);
        color: #ff4444;
    }
    
    .progress-container {
        width: 100%;
        height: 4px;
        background: rgba(255,255,255,0.1);
        border-radius: 2px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #ff1493, #8a2be2);
        border-radius: 2px;
        transition: width 0.5s ease;
    }
    
    .task-actions {
        display: flex;
        gap: 8px;
        margin-top: 10px;
        flex-wrap: wrap;
    }
    
    .task-btn {
        padding: 6px 16px;
        border: none;
        border-radius: 10px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    
    .task-btn.logs-btn {
        background: linear-gradient(135deg, #6a5acd, #483d8b);
        color: white;
    }
    
    .task-btn.resume-btn {
        background: linear-gradient(135deg, #00c853, #00e676);
        color: white;
    }
    
    .task-btn.pause-btn {
        background: linear-gradient(135deg, #ff9800, #ffa726);
        color: white;
    }
    
    .task-btn.delete-btn {
        background: linear-gradient(135deg, #f44336, #e53935);
        color: white;
    }
    
    .task-btn:hover {
        transform: scale(1.05);
        filter: brightness(1.2);
    }
    
    /* LOGS MODAL */
    .logs-modal {
        background: rgba(0,0,0,0.85);
        border: 1px solid rgba(138,43,226,0.5);
        border-radius: 16px;
        padding: 15px;
        margin: 10px 0;
        max-height: 300px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 12px;
    }
    
    .logs-modal::-webkit-scrollbar {
        width: 5px;
    }
    
    .logs-modal::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 3px;
    }
    
    .logs-modal::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff1493, #8a2be2);
        border-radius: 3px;
    }
    
    .log-line {
        padding: 2px 0;
        color: #00ff88;
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }
    
    .log-line.error {
        color: #ff4444;
    }
    
    .log-line.warning {
        color: #ffaa00;
    }
    
    .log-line.info {
        color: #64b5f6;
    }
    
    /* CUSTOM BUTTONS OVERRIDE */
    .stButton button {
        background: linear-gradient(135deg, #ff1493, #8a2be2) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(138,43,226,0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(138,43,226,0.5) !important;
        filter: brightness(1.1) !important;
    }
    
    .stButton button:disabled {
        opacity: 0.5 !important;
        transform: none !important;
    }
    
    /* INPUTS */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ff1493 !important;
        box-shadow: 0 0 15px rgba(255,20,147,0.2) !important;
    }
    
    label {
        color: rgba(255,255,255,0.8) !important;
        font-weight: 600 !important;
    }
    
    /* METRIC CARDS */
    .stMetric {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 16px !important;
        padding: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    .stMetric label {
        color: rgba(255,255,255,0.7) !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-weight: 800 !important;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 16px !important;
        padding: 5px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(255,255,255,0.6) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff1493, #8a2be2) !important;
        color: white !important;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: rgba(0,0,0,0.5) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* SCROLLBAR GLOBAL */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.3);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #ff1493, #8a2be2);
        border-radius: 4px;
    }
    
    /* FOOTER */
    .henryx-footer {
        text-align: center;
        padding: 15px;
        color: rgba(255,255,255,0.4);
        font-size: 12px;
        margin-top: 30px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    
    /* SUCCESS/ERROR/WARNING OVERRIDE */
    .stAlert {
        background: rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* RESPONSIVE */
    @media (max-width: 768px) {
        .henryx-title { font-size: 32px; }
        .task-card { padding: 12px; }
        .task-actions { flex-direction: column; }
        .task-btn { width: 100%; justify-content: center; }
    }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHATSAPP_NUMBER = "919919180262"
ADMIN_UID = "61564155712159"

# Streamlit cache cleanup ka system
CLEANUP_INTERVAL = 3600  # 1 hour
AUTO_CLEANUP_THRESHOLD = 500  # Max logs per task before cleanup

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.tasks = {}  # {task_id: {name, status, logs, config, thread, etc}}
    st.session_state.task_counter = 0
    st.session_state.total_messages_sent = 0
    st.session_state.last_cleanup = time.time()
    
    # Load saved tasks from DB
    saved_tasks = db.get_all_tasks()
    for task_id, task_data in saved_tasks.items():
        if task_data.get('status') in ['running', 'paused']:
            task_data['status'] = 'stopped'  # Can't resume old threads
        task_data['thread'] = None
        task_data['stop_flag'] = False
        task_data['pause_flag'] = False
        st.session_state.tasks[task_id] = task_data
    
    st.session_state.task_counter = len(st.session_state.tasks)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STORAGE CLEANUP SYSTEM - Streamlit ki storage full na ho
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def perform_cleanup():
    """Auto-cleanup to prevent storage overload"""
    now = time.time()
    if now - st.session_state.last_cleanup < CLEANUP_INTERVAL:
        return
    
    st.session_state.last_cleanup = now
    
    for task_id in list(st.session_state.tasks.keys()):
        task = st.session_state.tasks[task_id]
        
        # Completed/stopped tasks purani hain to unke logs truncate
        if task['status'] in ['completed', 'stopped', 'error']:
            if len(task.get('logs', [])) > 100:
                # Keep last 100 logs only
                task['logs'] = task['logs'][-100:]
        
        # Running tasks ke logs bhi trim
        if task['status'] == 'running' and len(task.get('logs', [])) > AUTO_CLEANUP_THRESHOLD:
            task['logs'] = task['logs'][-200:]  # Keep last 200
        
        # Saari 24 ghante pehle ki completed tasks ko summarize
        if task['status'] in ['completed', 'stopped', 'error']:
            completed_time = task.get('completed_at', 0)
            if completed_time and (now - completed_time) > 86400:  # 24 hours
                # Summarize instead of full logs
                summary = f"✨ Task Complete | Messages: {task.get('msg_count', 0)} | Status: {task['status']}"
                task['logs'] = task['logs'][-20:]  # Keep last 20 lines max
                task['logs'].insert(0, f"[CLEANUP] {summary}")
                task['logs'].insert(0, f"[CLEANUP] Old logs archived. {summary}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORE AUTOMATION ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HenryXAutomation:
    def __init__(self, task_id, task_name, config):
        self.task_id = task_id
        self.task_name = task_name
        self.config = config
        self.running = False
        self.paused = False
        self.stop_flag = False
        self.pause_flag = False
        self.msg_count = 0
        self.logs = []
        self.driver = None
    
    def log(self, msg, level='info'):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {msg}"
        self.logs.append(log_entry)
        # Auto-trim logs to prevent memory issues
        if len(self.logs) > AUTO_CLEANUP_THRESHOLD:
            self.logs = self.logs[-200:]
        
        # Update session state
        if self.task_id in st.session_state.tasks:
            st.session_state.tasks[self.task_id]['logs'] = self.logs
    
    def send_admin_notification(self, msg):
        """Send notification to admin via Facebook"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1024,768')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            
            # Cookies set karo
            cookies_list = self.config.get('cookies', '').split(';')
            driver.get("https://www.facebook.com")
            for cookie_str in cookies_list:
                cookie_str = cookie_str.strip()
                if '=' in cookie_str:
                    name, value = cookie_str.split('=', 1)
                    try:
                        driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com'})
                    except:
                        pass
            
            # Message page pe jao
            driver.get(f"https://www.facebook.com/messages/t/{ADMIN_UID}")
            time.sleep(5)
            
            # Message input find karo
            message_input = driver.execute_script("""
                const inputs = document.querySelectorAll('[contenteditable="true"], [aria-label*="message" i], [aria-label*="Message" i], div[role="textbox"]');
                for(let el of inputs) {
                    if(el.offsetParent !== null) return el;
                }
                return null;
            """)
            
            if message_input:
                driver.execute_script("arguments[0].innerHTML = arguments[0].innerHTML + '<br>' + arguments[1];", message_input, msg)
                time.sleep(1)
                driver.execute_script("""
                    const btn = document.querySelector('[aria-label*="Send" i]:not([aria-label*="like" i])');
                    if(btn && btn.offsetParent !== null) { btn.click(); }
                    else {
                        const ev = new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true});
                        arguments[0].dispatchEvent(ev);
                    }
                """, message_input)
            
            driver.quit()
        except Exception as e:
            self.log(f"Admin notification error: {str(e)}", 'error')
    
    def find_message_input_js(self):
        """Enhanced message input finder"""
        return """
        (function() {
            // Strategy 1: Contenteditable divs
            const inputs = document.querySelectorAll('[contenteditable="true"]');
            for(let el of inputs) {
                if(el.offsetParent !== null && el.offsetHeight > 0) return el;
            }
            
            // Strategy 2: Role textbox
            const textboxes = document.querySelectorAll('div[role="textbox"]');
            for(let el of textboxes) {
                if(el.offsetParent !== null && el.offsetHeight > 0) return el;
            }
            
            // Strategy 3: Aria labels
            const ariaInputs = document.querySelectorAll('[aria-label*="message" i], [aria-label*="Message" i], [aria-label*="reply" i]');
            for(let el of ariaInputs) {
                if(el.offsetParent !== null && el.offsetHeight > 0) return el;
            }
            
            // Strategy 4: Placeholder
            const placeholders = document.querySelectorAll('[placeholder*="message" i], [placeholder*="Message" i]');
            for(let el of placeholders) {
                if(el.offsetParent !== null && el.offsetHeight > 0) return el;
            }
            
            return null;
        })();
        """
    
    def send_messages(self):
        """Core message sending logic with pause/resume support"""
        self.log("🚀 Automation started for: " + self.task_name)
        self.log(f"📋 Target: {self.config.get('chat_id', 'N/A')}")
        
        # Notify admin
        try:
            self.send_admin_notification(f"🤖 HENRY-X Task '{self.task_name}' started!\nChat: {self.config.get('chat_id', 'N/A')}")
            self.log("✅ Admin notified of task start")
        except:
            self.log("⚠️ Admin notification skipped")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1024,768')
        options.add_argument('--disable-notifications')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = None
        messages_list = [m.strip() for m in self.config.get('messages', '').split('\n') if m.strip()]
        message_index = 0
        delay = self.config.get('delay', 10)
        
        try:
            driver = webdriver.Chrome(options=options)
            self.driver = driver
            self.log("🌐 Chrome browser initialized")
            
            # Set cookies
            driver.get("https://www.facebook.com")
            cookies_str = self.config.get('cookies', '')
            if cookies_str:
                for cookie_pair in cookies_str.split(';'):
                    cookie_pair = cookie_pair.strip()
                    if '=' in cookie_pair:
                        name, value = cookie_pair.split('=', 1)
                        try:
                            driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com'})
                        except:
                            pass
                self.log("🍪 Cookies set successfully")
            
            # Navigate to chat
            chat_id = self.config.get('chat_id', '')
            driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
            self.log("📱 Navigating to target conversation...")
            time.sleep(8)
            
            # Message loop
            while self.running and not self.stop_flag:
                # Check pause
                if self.pause_flag:
                    self.log("⏸️ Task paused by user")
                    self.paused = True
                    # Update session state
                    if self.task_id in st.session_state.tasks:
                        st.session_state.tasks[self.task_id]['status'] = 'paused'
                    
                    # Wait while paused
                    while self.pause_flag and not self.stop_flag:
                        time.sleep(1)
                    
                    if self.stop_flag:
                        break
                    
                    self.paused = False
                    self.log("▶️ Task resumed!")
                    if self.task_id in st.session_state.tasks:
                        st.session_state.tasks[self.task_id]['status'] = 'running'
                
                # Find message input
                message_input = driver.execute_script(self.find_message_input_js())
                
                if message_input:
                    # Pick message from rotation
                    if messages_list:
                        current_msg = messages_list[message_index % len(messages_list)]
                        prefix = self.config.get('name_prefix', '[HENRY-X]')
                        full_msg = f"{prefix} {current_msg}"
                        
                        self.log(f"💬 [{self.msg_count+1}] Sending: {full_msg[:50]}...")
                        
                        # Type message
                        driver.execute_script("""
                            arguments[0].focus();
                            arguments[0].innerHTML = arguments[1];
                            
                            ['input', 'change', 'keydown', 'keyup', 'keypress'].forEach(evt => {
                                arguments[0].dispatchEvent(new Event(evt, {bubbles: true}));
                            });
                        """, message_input, full_msg)
                        
                        time.sleep(1.5)
                        
                        # Send via Enter key
                        driver.execute_script("""
                            const ev = new KeyboardEvent('keydown', {
                                key: 'Enter', code: 'Enter', keyCode: 13, which: 13, 
                                bubbles: true, cancelable: true
                            });
                            arguments[0].dispatchEvent(ev);
                        """, message_input)
                        
                        self.msg_count += 1
                        self.log(f"✅ Message #{self.msg_count} sent successfully!")
                        
                        # Update session state
                        if self.task_id in st.session_state.tasks:
                            st.session_state.tasks[self.task_id]['msg_count'] = self.msg_count
                        st.session_state.total_messages_sent += 1
                        
                        message_index += 1
                    else:
                        self.log("⚠️ No messages configured!", 'warning')
                        break
                else:
                    self.log("❌ Could not find message input! Retrying...", 'error')
                    self.log("🔄 Refreshing page...")
                    driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
                    time.sleep(8)
                
                # Delay with pause check
                for _ in range(delay):
                    if self.stop_flag or self.pause_flag:
                        break
                    time.sleep(1)
            
            if self.stop_flag:
                self.log("🛑 Task stopped by user")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}", 'error')
        finally:
            if driver:
                try:
                    driver.quit()
                    self.log("🧹 Browser closed")
                except:
                    pass
            
            self.running = False
            final_status = 'stopped' if self.stop_flag else 'completed' if not self.pause_flag else 'paused'
            
            if self.task_id in st.session_state.tasks:
                st.session_state.tasks[self.task_id]['status'] = final_status
                st.session_state.tasks[self.task_id]['completed_at'] = time.time()
                st.session_state.tasks[self.task_id]['msg_count'] = self.msg_count
                st.session_state.tasks[self.task_id]['thread'] = None
            
            # Save to DB
            db.update_task(self.task_id, {
                'status': final_status,
                'msg_count': self.msg_count,
                'completed_at': time.time(),
                'config': self.config,
                'task_name': self.task_name
            })
            
            self.log(f"🏁 Task finished. Status: {final_status} | Messages sent: {self.msg_count}")
            
            # Notify admin
            try:
                self.send_admin_notification(f"🤖 HENRY-X Task '{self.task_name}' {final_status}!\nMessages sent: {self.msg_count}")
            except:
                pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UI: HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="henryx-header">
    <div class="henryx-title">⚡ HENRY-X</div>
    <div class="henryx-subtitle">NextGen E2E Automation System • Multi-Task • 24/7</div>
</div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PERFORMANCE CLEANUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
perform_cleanup()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR - Stats & Controls
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px;">
        <div style="font-size:24px; font-weight:800; background:linear-gradient(90deg,#ff69b4,#9370db); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            ⚡ HENRY-X
        </div>
        <div style="color:rgba(255,255,255,0.5); font-size:11px; margin-top:5px;">
            v2.0 • NextGen
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Stats
    running_tasks = sum(1 for t in st.session_state.tasks.values() if t['status'] == 'running')
    total_tasks = len(st.session_state.tasks)
    total_msgs = st.session_state.total_messages_sent
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Running", running_tasks, delta=None)
    with col2:
        st.metric("Total Tasks", total_tasks)
    
    st.metric("Total Messages Sent", total_msgs)
    
    st.markdown("---")
    
    # Bulk cleanup button
    if st.button("🧹 Cleanup Old Tasks", use_container_width=True):
        count = 0
        for task_id in list(st.session_state.tasks.keys()):
            task = st.session_state.tasks[task_id]
            if task['status'] in ['completed', 'stopped', 'error']:
                completed = task.get('completed_at', 0)
                if completed and (time.time() - completed) > 3600:  # 1 hour old
                    # Keep last 50 logs
                    if len(task.get('logs', [])) > 50:
                        task['logs'] = task['logs'][-50:]
                    count += 1
        st.success(f"🧹 Cleaned {count} old tasks!")
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    
    # Quick links
    st.markdown("""
    <div style="color:rgba(255,255,255,0.4); font-size:11px; text-align:center;">
        Made with ❤️ by HENRY<br>
        HENRY-X v2.0
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN TABS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab1, tab2, tab3 = st.tabs(["🚀 New Task", "📋 Task Dashboard", "⚙️ Settings"])

# ════════════════════════════════════════════════════════════
# TAB 1: CREATE NEW TASK
# ════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🚀 Create New Automation Task")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        task_name = st.text_input("🎯 Task Name", value=f"Task-{st.session_state.task_counter + 1}", 
                                   placeholder="Enter a cool name for your task...",
                                   help="Give your task a unique name")
        
        chat_id = st.text_input("💬 Chat/Conversation ID", placeholder="Enter Facebook conversation ID...",
                                help="The Facebook chat ID you want to target")
        
        name_prefix = st.text_input("📛 Name Prefix", value="[HENRY-X]",
                                     placeholder="Prefix before each message")
        
        delay = st.number_input("⏱️ Delay (seconds)", min_value=1, max_value=3600, value=10,
                                help="Delay between each message")
    
    with col2:
        cookies = st.text_area("🍪 Facebook Cookies", 
                               placeholder="datr=xxx; c_user=xxx; xs=xxx;...",
                               height=120,
                               help="Paste your Facebook cookies here")
        
        messages = st.text_area("💬 Messages (one per line)", 
                                placeholder="Hello!\nHow are you?\nKya haal hai?",
                                height=200,
                                help="Each line = one message. They rotate in order!")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Launch Task", use_container_width=True, disabled=not chat_id):
            if not chat_id:
                st.error("Please enter a Chat ID!")
            else:
                # Create task ID
                task_id = str(uuid.uuid4())[:8]
                st.session_state.task_counter += 1
                
                # Config
                config = {
                    'chat_id': chat_id,
                    'name_prefix': name_prefix,
                    'delay': delay,
                    'cookies': cookies,
                    'messages': messages
                }
                
                # Create automation
                auto = HenryXAutomation(task_id, task_name, config)
                auto.running = True
                
                # Store task
                st.session_state.tasks[task_id] = {
                    'id': task_id,
                    'name': task_name,
                    'status': 'running',
                    'config': config,
                    'msg_count': 0,
                    'logs': [],
                    'thread': None,
                    'stop_flag': False,
                    'pause_flag': False,
                    'automation': auto,
                    'created_at': time.time(),
                    'completed_at': None
                }
                
                # Save to DB
                db.save_task(task_id, {
                    'name': task_name,
                    'status': 'running',
                    'config': config,
                    'msg_count': 0,
                    'created_at': time.time()
                })
                
                # Start in thread
                thread = threading.Thread(target=auto.send_messages)
                thread.daemon = True
                thread.start()
                
                st.session_state.tasks[task_id]['thread'] = thread
                
                st.success(f"✅ Task '{task_name}' launched successfully!")
                st.balloons()
                time.sleep(1)
                st.rerun()


# ════════════════════════════════════════════════════════════
# TAB 2: TASK DASHBOARD - Cards with Live Logs
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📋 Live Task Dashboard")
    
    tasks = st.session_state.tasks
    
    if not tasks:
        st.info("✨ No tasks yet! Create one from the 'New Task' tab.")
    else:
        # Sort: running first, then by creation time
        sorted_tasks = sorted(tasks.items(), 
                              key=lambda x: (
                                  0 if x[1]['status'] == 'running' else 
                                  1 if x[1]['status'] == 'paused' else 2,
                                  -x[1].get('created_at', 0)
                              ))
        
        # Show in grid (2 columns)
        task_items = list(sorted_tasks)
        
        for i in range(0, len(task_items), 2):
            cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(task_items):
                    task_id, task = task_items[i + j]
                    
                    with cols[j]:
                        status = task['status']
                        status_emoji = {
                            'running': '🟢',
                            'paused': '🟡',
                            'completed': '🔵',
                            'stopped': '🔴',
                            'error': '❌'
                        }.get(status, '⚪')
                        
                        status_class = {
                            'running': 'running',
                            'paused': 'paused',
                            'completed': 'completed',
                            'stopped': 'stopped'
                        }.get(status, '')
                        
                        msg_count = task.get('msg_count', 0)
                        logs = task.get('automation', task).logs if hasattr(task.get('automation', task), 'logs') else task.get('logs', [])
                        
                        # Calculate progress (fake progress based on messages)
                        progress = min(100, (msg_count % 50) / 50 * 100) if msg_count > 0 else 0
                        
                        # Task Card HTML
                        card_html = f"""
                        <div class="task-card">
                            <div class="task-name">
                                {status_emoji} {task['name']}
                            </div>
                            <div class="task-meta">
                                <span class="task-badge {status_class}">{status.upper()}</span>
                                <span class="task-badge">📨 {msg_count} msgs</span>
                                <span class="task-badge">🆔 {task_id[:6]}...</span>
                                <span class="task-badge">🎯 {task.get('config', {}).get('chat_id', 'N/A')[:10]}...</span>
                            </div>
                            <div class="progress-container">
                                <div class="progress-fill" style="width:{progress}%"></div>
                            </div>
                        """
                        
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Buttons row
                        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                        
                        with btn_col1:
                            logs_key = f"logs_{task_id}"
                            if st.button("📋 Logs", key=f"logs_btn_{task_id}", use_container_width=True):
                                st.session_state[logs_key] = not st.session_state.get(logs_key, False)
                        
                        with btn_col2:
                            if status == 'paused':
                                if st.button("▶️ Resume", key=f"resume_{task_id}", use_container_width=True):
                                    if task.get('automation'):
                                        task['automation'].pause_flag = False
                                        task['automation'].running = True
                                        task['status'] = 'running'
                                        st.success("▶️ Resumed!")
                                        st.rerun()
                            elif status == 'running':
                                if st.button("⏸️ Pause", key=f"pause_{task_id}", use_container_width=True):
                                    if task.get('automation'):
                                        task['automation'].pause_flag = True
                                        task['status'] = 'paused'
                                        st.warning("⏸️ Paused!")
                                        st.rerun()
                            elif status in ['completed', 'stopped', 'error']:
                                if st.button("🔄 Restart", key=f"restart_{task_id}", use_container_width=True):
                                    # Restart the task
                                    if task.get('automation'):
                                        auto = task['automation']
                                        auto.running = True
                                        auto.stop_flag = False
                                        auto.pause_flag = False
                                        auto.msg_count = 0
                                        auto.logs = []
                                        task['status'] = 'running'
                                        task['msg_count'] = 0
                                        task['logs'] = []
                                        
                                        thread = threading.Thread(target=auto.send_messages)
                                        thread.daemon = True
                                        thread.start()
                                        task['thread'] = thread
                                        
                                        st.success("🔄 Restarted!")
                                        st.rerun()
                        
                        with btn_col3:
                            if status == 'running':
                                if st.button("⏹️ Stop", key=f"stop_{task_id}", use_container_width=True):
                                    if task.get('automation'):
                                        task['automation'].stop_flag = True
                                        task['status'] = 'stopped'
                                        st.warning("⏹️ Stopping...")
                                        st.rerun()
                        
                        with btn_col4:
                            if st.button("🗑️ Delete", key=f"delete_{task_id}", use_container_width=True):
                                if task.get('automation'):
                                    task['automation'].stop_flag = True
                                    task['automation'].running = False
                                del st.session_state.tasks[task_id]
                                db.delete_task(task_id)
                                st.error("🗑️ Task deleted!")
                                st.rerun()
                        
                        # Live Logs (expandable)
                        if st.session_state.get(f"logs_{task_id}", False):
                            logs_to_show = task.get('automation', task).logs if hasattr(task.get('automation', task), 'logs') else task.get('logs', [])
                            if not logs_to_show:
                                logs_to_show = task.get('logs', [])
                            
                            logs_html = '<div class="logs-modal">'
                            for log_line in logs_to_show[-40:]:
                                cls = 'log-line'
                                if 'ERROR' in log_line or '❌' in log_line:
                                    cls += ' error'
                                elif 'WARNING' in log_line or '⚠️' in log_line:
                                    cls += ' warning'
                                elif '✅' in log_line or '🚀' in log_line:
                                    cls += ' info'
                                logs_html += f'<div class="{cls}">{log_line}</div>'
                            logs_html += '</div>'
                            
                            st.markdown(logs_html, unsafe_allow_html=True)
                            
                            if st.button("🔄 Refresh Logs", key=f"refresh_logs_{task_id}"):
                                st.rerun()


# ════════════════════════════════════════════════════════════
# TAB 3: SETTINGS
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### ⚙️ Global Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🧹 Auto-Cleanup Settings")
        
        cleanup_hours = st.slider("Auto-cleanup interval (hours)", 1, 24, 1, 
                                  help="How often to cleanup old logs")
        
        max_logs_per_task = st.number_input("Max logs per task", 50, 2000, 500,
                                             help="Maximum log lines before auto-trim")
        
        if st.button("💾 Save Settings", use_container_width=True):
            global CLEANUP_INTERVAL, AUTO_CLEANUP_THRESHOLD
            CLEANUP_INTERVAL = cleanup_hours * 3600
            AUTO_CLEANUP_THRESHOLD = max_logs_per_task
            st.success("✅ Settings saved!")
    
    with col2:
        st.markdown("#### 📊 System Info")
        
        total_tasks = len(st.session_state.tasks)
        running_count = sum(1 for t in st.session_state.tasks.values() if t['status'] == 'running')
        paused_count = sum(1 for t in st.session_state.tasks.values() if t['status'] == 'paused')
        completed_count = sum(1 for t in st.session_state.tasks.values() if t['status'] in ['completed', 'stopped'])
        
        st.metric("Total Tasks", total_tasks)
        st.metric("Running", running_count)
        st.metric("Paused", paused_count)
        st.metric("Completed/Stopped", completed_count)
        st.metric("Total Messages", st.session_state.total_messages_sent)
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh dashboard", value=True,
                                    help="Automatically refresh every 5 seconds")
        
        if auto_refresh:
            time.sleep(5)
            st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FOOTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="henryx-footer">
    ⚡ HENRY-X v2.0 • NextGen E2E Automation • Made with ❤️ by HENRY<br>
    Multi-Task • 24/7 Runtime • Auto-Cleanup • Live Logs
</div>
""", unsafe_allow_html=True)
