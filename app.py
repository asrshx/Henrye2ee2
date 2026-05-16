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
import atexit

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
    .stApp {
        background: linear-gradient(135deg, #ff1493 0%, #8a2be2 50%, #4a0080 100%) !important;
        background-attachment: fixed !important;
    }
    .main > div {
        background: rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 20px !important;
        margin: 10px 0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
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
    .logs-modal::-webkit-scrollbar { width: 5px; }
    .logs-modal::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); border-radius: 3px; }
    .logs-modal::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #ff1493, #8a2be2); border-radius: 3px; }
    .log-line { padding: 2px 0; color: #00ff88; border-bottom: 1px solid rgba(255,255,255,0.03); }
    .log-line.error { color: #ff4444; }
    .log-line.warning { color: #ffaa00; }
    .log-line.info { color: #64b5f6; }
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
    }
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    label { color: rgba(255,255,255,0.8) !important; font-weight: 600 !important; }
    .stMetric {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 16px !important;
        padding: 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    .stMetric label { color: rgba(255,255,255,0.7) !important; }
    .stMetric [data-testid="stMetricValue"] { color: white !important; font-weight: 800 !important; }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 16px !important;
        padding: 5px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    .stTabs [data-baseweb="tab"] { color: rgba(255,255,255,0.6) !important; border-radius: 12px !important; font-weight: 600 !important; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #ff1493, #8a2be2) !important; color: white !important; }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #ff1493, #8a2be2); border-radius: 4px; }
    .henryx-footer { text-align: center; padding: 15px; color: rgba(255,255,255,0.4); font-size: 12px; margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.05); }
    @media (max-width: 768px) { .henryx-title { font-size: 32px; } .task-card { padding: 12px; } }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHARED STATE (Thread-Safe) - FIX: Threads st.session_state touch nahi karenge
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tasks_data = {}  # Global dict for threads to write to (thread-safe)
tasks_data_lock = threading.Lock()
total_messages_sent_global = 0
total_msgs_lock = threading.Lock()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE INIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.tasks = {}
    st.session_state.task_counter = 0
    st.session_state.total_messages_sent = 0
    st.session_state.last_cleanup = time.time()
    st.session_state.cleanup_interval = 3600
    st.session_state.auto_cleanup_threshold = 500
    
    # Load saved tasks
    saved_tasks = db.get_all_tasks()
    for task_id, task_data in saved_tasks.items():
        if task_data.get('status') in ['running', 'paused']:
            task_data['status'] = 'stopped'
        task_data['stop_flag'] = False
        task_data['pause_flag'] = False
        st.session_state.tasks[task_id] = task_data
        # Thread mein sync bhi karo
        with tasks_data_lock:
            tasks_data[task_id] = {
                'logs': [],
                'msg_count': task_data.get('msg_count', 0),
                'status': task_data['status']
            }
    
    st.session_state.task_counter = len(st.session_state.tasks)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTO CLEANUP (Main thread se)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def perform_cleanup():
    now = time.time()
    cleanup_interval = st.session_state.get('cleanup_interval', 3600)
    auto_cleanup_threshold = st.session_state.get('auto_cleanup_threshold', 500)
    
    if now - st.session_state.last_cleanup < cleanup_interval:
        return
    
    st.session_state.last_cleanup = now
    
    for task_id in list(st.session_state.tasks.keys()):
        task = st.session_state.tasks[task_id]
        if task['status'] in ['completed', 'stopped', 'error']:
            if len(task.get('logs', [])) > 100:
                task['logs'] = task['logs'][-100:]
        if task['status'] == 'running' and len(task.get('logs', [])) > auto_cleanup_threshold:
            task['logs'] = task['logs'][-200:]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SYNC: Thread -> Session State (UI refresh se pehle call karo)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def sync_thread_data_to_session():
    """Threads apna data tasks_data dict mein likhte hain, 
    ye function use session state mein sync karta hai jab UI render ho"""
    with tasks_data_lock:
        for task_id, thread_data in tasks_data.items():
            if task_id in st.session_state.tasks:
                st.session_state.tasks[task_id]['logs'] = thread_data.get('logs', [])
                st.session_state.tasks[task_id]['msg_count'] = thread_data.get('msg_count', 0)
                status = thread_data.get('status')
                if status:
                    st.session_state.tasks[task_id]['status'] = status
    
    with total_msgs_lock:
        st.session_state.total_messages_sent = total_messages_sent_global


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTOMATION ENGINE (Thread-Safe - No st.session_state)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def start_automation_thread(task_id, task_name, config):
    """This runs in a SEPARATE thread. NO st.session_state here!"""
    
    # Thread-safe logs store karne ke liye
    local_logs = []
    local_msg_count = 0
    
    def log(msg, level='info'):
        nonlocal local_logs
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {msg}"
        local_logs.append(log_entry)
        # Trim
        if len(local_logs) > 500:
            local_logs = local_logs[-200:]
        
        # Sync to shared dict
        with tasks_data_lock:
            if task_id in tasks_data:
                tasks_data[task_id]['logs'] = local_logs
    
    def update_status(status):
        with tasks_data_lock:
            if task_id in tasks_data:
                tasks_data[task_id]['status'] = status
    
    def update_msg_count(count):
        nonlocal local_msg_count
        local_msg_count = count
        with tasks_data_lock:
            if task_id in tasks_data:
                tasks_data[task_id]['msg_count'] = count
    
    def send_admin_notification(msg):
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1024,768')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            cookies_str = config.get('cookies', '')
            driver.get("https://www.facebook.com")
            if cookies_str:
                for cookie_pair in cookies_str.split(';'):
                    cookie_pair = cookie_pair.strip()
                    if '=' in cookie_pair:
                        name, value = cookie_pair.split('=', 1)
                        try:
                            driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com'})
                        except:
                            pass
            
            driver.get(f"https://www.facebook.com/messages/t/61564155712159")
            time.sleep(5)
            
            message_input = driver.execute_script("""
                const inputs = document.querySelectorAll('[contenteditable="true"], [aria-label*="message" i], div[role="textbox"]');
                for(let el of inputs) {
                    if(el.offsetParent !== null) return el;
                }
                return null;
            """)
            
            if message_input:
                driver.execute_script("arguments[0].innerHTML = arguments[1];", message_input, msg)
                time.sleep(1)
                driver.execute_script("""
                    const ev = new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true});
                    arguments[0].dispatchEvent(ev);
                """, message_input)
            
            driver.quit()
        except Exception as e:
            log(f"Admin notification error: {str(e)}", 'error')
    
    ## ── Main Logic ──
    log(f"🚀 Automation started for: {task_name}")
    log(f"📋 Target: {config.get('chat_id', 'N/A')}")
    
    try:
        send_admin_notification(f"🤖 HENRY-X Task '{task_name}' started!\nChat: {config.get('chat_id', 'N/A')}")
        log("✅ Admin notified")
    except:
        log("⚠️ Admin notification skipped")
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1024,768')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.binary_location = '/usr/bin/chromium'
    
    driver = None
    messages_list = [m.strip() for m in config.get('messages', '').split('\n') if m.strip()]
    message_index = 0
    delay = config.get('delay', 10)
    
    def should_stop():
        with tasks_data_lock:
            return tasks_data.get(task_id, {}).get('stop_flag', False)
    
    def should_pause():
        with tasks_data_lock:
            return tasks_data.get(task_id, {}).get('pause_flag', False)
    
    try:
        # WebDriver Manager se init karo
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        log("🌐 Chrome browser initialized successfully!")
        
        # Cookies
        driver.get("https://www.facebook.com")
        log("🌍 Facebook loaded")
        time.sleep(3)
        
        cookies_str = config.get('cookies', '')
        if cookies_str:
            success_count = 0
            for cookie_pair in cookies_str.split(';'):
                cookie_pair = cookie_pair.strip()
                if '=' in cookie_pair:
                    name, value = cookie_pair.split('=', 1)
                    try:
                        driver.add_cookie({'name': name.strip(), 'value': value.strip(), 'domain': '.facebook.com'})
                        success_count += 1
                    except Exception as e:
                        log(f"Cookie error for {name}: {str(e)[:30]}", 'warning')
            log(f"🍪 {success_count} cookies set")
        else:
            log("⚠️ No cookies provided!", 'warning')
        
        chat_id = config.get('chat_id', '')
        driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
        log(f"📱 Navigating to chat: {chat_id}")
        time.sleep(8)
        
        # Page title check - ensure loaded
        title = driver.title
        log(f"📄 Page title: {title}")
        
        while not should_stop():
            while should_pause() and not should_stop():
                update_status('paused')
                log("⏸️ Paused...")
                time.sleep(2)
            
            if should_stop():
                break
            
            update_status('running')
            
            # Find message input
            message_input = driver.execute_script("""
                (function() {
                    const selectors = [
                        '[contenteditable="true"]',
                        'div[role="textbox"]',
                        '[aria-label*="message" i]',
                        '[aria-label*="Message" i]',
                        '[aria-label*="reply" i]',
                        '[placeholder*="message" i]',
                        '[placeholder*="Message" i]'
                    ];
                    for(let sel of selectors) {
                        let els = document.querySelectorAll(sel);
                        for(let el of els) {
                            if(el.offsetParent !== null && el.offsetHeight > 5) return el;
                        }
                    }
                    return null;
                })();
            """)
            
            if message_input and messages_list:
                current_msg = messages_list[message_index % len(messages_list)]
                prefix = config.get('name_prefix', '[HENRY-X]')
                full_msg = f"{prefix} {current_msg}"
                local_msg_count += 1
                
                log(f"💬 [{local_msg_count}] Sending: {full_msg[:40]}...")
                
                driver.execute_script("""
                    arguments[0].focus();
                    arguments[0].innerHTML = arguments[1];
                    ['input','change','keydown','keyup','keypress','textInput'].forEach(evt => {
                        arguments[0].dispatchEvent(new Event(evt, {bubbles: true, cancelable: true}));
                    });
                """, message_input, full_msg)
                time.sleep(1.5)
                
                driver.execute_script("""
                    const ev = new KeyboardEvent('keydown', {
                        key:'Enter', code:'Enter', keyCode:13, which:13,
                        bubbles:true, cancelable:true
                    });
                    arguments[0].dispatchEvent(ev);
                """, message_input)
                
                log(f"✅ Message #{local_msg_count} sent!")
                update_msg_count(local_msg_count)
                
                with total_msgs_lock:
                    global total_messages_sent_global
                    total_messages_sent_global += 1
                
                message_index += 1
            elif not message_input:
                log("❌ Message input not found!", 'error')
                log("🔄 Refreshing page...")
                driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
                time.sleep(8)
            else:
                log("⚠️ No messages in config!", 'warning')
                break
            
            for _ in range(delay):
                if should_stop() or should_pause():
                    break
                time.sleep(1)
        
    except Exception as e:
        log(f"❌ CRASHED: {str(e)}", 'error')
        import traceback
        log(f"📋 Trace: {traceback.format_exc()[:200]}", 'error')
    finally:
        if driver:
            try:
                driver.quit()
                log("🧹 Browser closed")
            except:
                pass
        
        if should_stop():
            final_status = 'stopped'
        elif should_pause():
            final_status = 'paused'
        else:
            final_status = 'completed'
        
        update_status(final_status)
        log(f"🏁 Task finished. Status: {final_status} | Messages: {local_msg_count}")
        
        # Save to DB
        db.update_task(task_id, {
            'status': final_status,
            'msg_count': local_msg_count,
            'completed_at': time.time(),
            'config': config,
            'task_name': task_name
        })
        
        # Clear stop/pause flags
        with tasks_data_lock:
            if task_id in tasks_data:
                tasks_data[task_id]['stop_flag'] = False
                tasks_data[task_id]['pause_flag'] = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UI: HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="henryx-header">
    <div class="henryx-title">⚡ HENRY-X</div>
    <div class="henryx-subtitle">NextGen E2E Automation System • Multi-Task • 24/7</div>
</div>
""", unsafe_allow_html=True)

# ── Sync thread data before rendering ──
sync_thread_data_to_session()

# ── Cleanup ──
perform_cleanup()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px;">
        <div style="font-size:24px; font-weight:800; background:linear-gradient(90deg,#ff69b4,#9370db); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            ⚡ HENRY-X
        </div>
        <div style="color:rgba(255,255,255,0.5); font-size:11px; margin-top:5px;">v2.0 • NextGen</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    running_tasks = sum(1 for t in st.session_state.tasks.values() if t['status'] == 'running')
    total_tasks = len(st.session_state.tasks)
    total_msgs = st.session_state.total_messages_sent
    
    col1, col2 = st.columns(2)
    with col1: st.metric("Running", running_tasks)
    with col2: st.metric("Total Tasks", total_tasks)
    st.metric("Total Messages Sent", total_msgs)
    
    st.markdown("---")
    
    if st.button("🧹 Cleanup Old Tasks", use_container_width=True):
        count = 0
        for task_id in list(st.session_state.tasks.keys()):
            task = st.session_state.tasks[task_id]
            if task['status'] in ['completed', 'stopped', 'error']:
                completed = task.get('completed_at', 0)
                if completed and (time.time() - completed) > 3600:
                    if len(task.get('logs', [])) > 50:
                        task['logs'] = task['logs'][-50:]
                    count += 1
        st.success(f"🧹 Cleaned {count} old tasks!")
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    st.markdown('<div style="color:rgba(255,255,255,0.4); font-size:11px; text-align:center;">Made with ❤️ by HENRY<br>HENRY-X v2.0</div>', unsafe_allow_html=True)


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
                                   placeholder="Enter a cool name for your task...")
        chat_id = st.text_input("💬 Chat/Conversation ID", placeholder="Enter Facebook conversation ID...")
        name_prefix = st.text_input("📛 Name Prefix", value="[HENRY-X]", placeholder="Prefix before each message")
        delay = st.number_input("⏱️ Delay (seconds)", min_value=1, max_value=3600, value=10)
    
    with col2:
        cookies = st.text_area("🍪 Facebook Cookies", 
                               placeholder="datr=xxx; c_user=xxx; xs=xxx;...",
                               height=120)
        messages = st.text_area("💬 Messages (one per line)", 
                                placeholder="Hello!\nHow are you?\nKya haal hai?",
                                height=200)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Launch Task", use_container_width=True, disabled=not chat_id):
            if not chat_id:
                st.error("Please enter a Chat ID!")
            else:
                task_id = str(uuid.uuid4())[:8]
                st.session_state.task_counter += 1
                
                config = {
                    'chat_id': chat_id,
                    'name_prefix': name_prefix,
                    'delay': delay,
                    'cookies': cookies,
                    'messages': messages
                }
                
                # Session state mein task create karo
                st.session_state.tasks[task_id] = {
                    'id': task_id,
                    'name': task_name,
                    'status': 'running',
                    'config': config,
                    'msg_count': 0,
                    'logs': [],
                    'created_at': time.time(),
                    'completed_at': None,
                    'stop_flag': False,
                    'pause_flag': False
                }
                
                # Shared dict mein bhi entry banao (thread access karega)
                with tasks_data_lock:
                    tasks_data[task_id] = {
                        'logs': [],
                        'msg_count': 0,
                        'status': 'running',
                        'stop_flag': False,
                        'pause_flag': False
                    }
                
                # DB mein save
                db.save_task(task_id, {
                    'name': task_name,
                    'status': 'running',
                    'config': config,
                    'msg_count': 0,
                    'created_at': time.time()
                })
                
                # Thread start karo
                thread = threading.Thread(
                    target=start_automation_thread,
                    args=(task_id, task_name, config)
                )
                thread.daemon = True
                thread.start()
                
                st.success(f"✅ Task '{task_name}' launched successfully!")
                st.balloons()
                time.sleep(1)
                st.rerun()
# ════════════════════════════════════════════════════════════
# TAB 2: TASK DASHBOARD
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📋 Live Task Dashboard")
    
    tasks = st.session_state.tasks
    
    if not tasks:
        st.info("✨ No tasks yet! Create one from the 'New Task' tab.")
    else:
        sorted_tasks = sorted(tasks.items(), 
                              key=lambda x: (
                                  0 if x[1]['status'] == 'running' else 
                                  1 if x[1]['status'] == 'paused' else 2,
                                  -x[1].get('created_at', 0)
                              ))
        
        task_items = list(sorted_tasks)
        
        for i in range(0, len(task_items), 2):
            cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(task_items):
                    task_id, task = task_items[i + j]
                    
                    with cols[j]:
                        status = task['status']
                        status_emoji = {
                            'running': '🟢', 'paused': '🟡', 'completed': '🔵',
                            'stopped': '🔴', 'error': '❌'
                        }.get(status, '⚪')
                        
                        status_class = {
                            'running': 'running', 'paused': 'paused',
                            'completed': 'completed', 'stopped': 'stopped'
                        }.get(status, '')
                        
                        msg_count = task.get('msg_count', 0)
                        logs = task.get('logs', [])
                        progress = min(100, (msg_count % 50) / 50 * 100) if msg_count > 0 else 0
                        
                        st.markdown(f"""
                        <div class="task-card">
                            <div class="task-name">{status_emoji} {task['name']}</div>
                            <div class="task-meta">
                                <span class="task-badge {status_class}">{status.upper()}</span>
                                <span class="task-badge">📨 {msg_count} msgs</span>
                                <span class="task-badge">🆔 {task_id[:6]}...</span>
                                <span class="task-badge">🎯 {task.get('config', {}).get('chat_id', 'N/A')[:10]}...</span>
                            </div>
                            <div class="progress-container">
                                <div class="progress-fill" style="width:{progress}%"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                        
                        with btn_col1:
                            logs_key = f"logs_{task_id}"
                            if st.button("📋 Logs", key=f"logs_btn_{task_id}", use_container_width=True):
                                st.session_state[logs_key] = not st.session_state.get(logs_key, False)
                        
                        with btn_col2:
                            if status == 'paused':
                                if st.button("▶️ Resume", key=f"resume_{task_id}", use_container_width=True):
                                    if task_id in tasks_data:
                                        with tasks_data_lock:
                                            if task_id in tasks_data:
                                                tasks_data[task_id]['pause_flag'] = False
                                    task['status'] = 'running'
                                    st.success("▶️ Resumed!")
                                    st.rerun()
                            elif status == 'running':
                                if st.button("⏸️ Pause", key=f"pause_{task_id}", use_container_width=True):
                                    if task_id in tasks_data:
                                        with tasks_data_lock:
                                            if task_id in tasks_data:
                                                tasks_data[task_id]['pause_flag'] = True
                                    task['status'] = 'paused'
                                    st.warning("⏸️ Paused!")
                                    st.rerun()
                            elif status in ['completed', 'stopped', 'error']:
                                if st.button("🔄 Restart", key=f"restart_{task_id}", use_container_width=True):
                                    if task_id in tasks_data:
                                        with tasks_data_lock:
                                            if task_id in tasks_data:
                                                tasks_data[task_id] = {
                                                    'logs': [],
                                                    'msg_count': 0,
                                                    'status': 'running',
                                                    'stop_flag': False,
                                                    'pause_flag': False
                                                }
                                    else:
                                        with tasks_data_lock:
                                            tasks_data[task_id] = {
                                                'logs': [],
                                                'msg_count': 0,
                                                'status': 'running',
                                                'stop_flag': False,
                                                'pause_flag': False
                                            }
                                    task['status'] = 'running'
                                    task['msg_count'] = 0
                                    task['logs'] = []
                                    
                                    thread = threading.Thread(
                                        target=start_automation_thread,
                                        args=(task_id, task['name'], task['config'])
                                    )
                                    thread.daemon = True
                                    thread.start()
                                    
                                    st.success("🔄 Restarted!")
                                    st.rerun()
                        
                        with btn_col3:
                            if status == 'running':
                                if st.button("⏹️ Stop", key=f"stop_{task_id}", use_container_width=True):
                                    if task_id in tasks_data:
                                        with tasks_data_lock:
                                            if task_id in tasks_data:
                                                tasks_data[task_id]['stop_flag'] = True
                                    task['status'] = 'stopped'
                                    st.warning("⏹️ Stopping...")
                                    st.rerun()
                        
                        with btn_col4:
                            if st.button("🗑️ Delete", key=f"delete_{task_id}", use_container_width=True):
                                # Stop thread if running
                                if task_id in tasks_data:
                                    with tasks_data_lock:
                                        if task_id in tasks_data:
                                            tasks_data[task_id]['stop_flag'] = True
                                
                                time.sleep(0.3)
                                
                                # Safely remove from all stores
                                if task_id in tasks_data:
                                    with tasks_data_lock:
                                        if task_id in tasks_data:
                                            del tasks_data[task_id]
                                
                                if task_id in st.session_state.tasks:
                                    del st.session_state.tasks[task_id]
                                
                                # Clean session state keys
                                keys_to_del = [k for k in st.session_state.keys() if task_id in str(k)]
                                for k in keys_to_del:
                                    del st.session_state[k]
                                
                                try:
                                    db.delete_task(task_id)
                                except:
                                    pass
                                
                                st.error("🗑️ Task deleted!")
                                st.rerun()
                        
                        # Live Logs
                        if st.session_state.get(f"logs_{task_id}", False):
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
        
        cleanup_hours = st.slider("Auto-cleanup interval (hours)", 1, 24, 
                                   value=st.session_state.get('cleanup_interval', 3600) // 3600)
        
        max_logs_per_task = st.number_input("Max logs per task", 50, 2000, 
                                              value=st.session_state.get('auto_cleanup_threshold', 500))
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.session_state.cleanup_interval = cleanup_hours * 3600
            st.session_state.auto_cleanup_threshold = max_logs_per_task
            st.success("✅ Settings saved!")
            st.rerun()
    
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
        
        auto_refresh = st.checkbox("🔄 Auto-refresh dashboard", value=True)
        
        if auto_refresh and running_count > 0:
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
