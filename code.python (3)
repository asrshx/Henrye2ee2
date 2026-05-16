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
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import database as db
import requests
import re
import traceback

st.set_page_config(
    page_title="HENRY-X • NextGen Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS THEME
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
    .task-badge.running { background: rgba(0,255,100,0.2); border-color: rgba(0,255,100,0.3); color: #00ff64; }
    .task-badge.paused { background: rgba(255,165,0,0.2); border-color: rgba(255,165,0,0.3); color: #ffa500; }
    .task-badge.completed { background: rgba(100,149,237,0.2); border-color: rgba(100,149,237,0.3); color: #6495ed; }
    .task-badge.stopped { background: rgba(255,0,0,0.2); border-color: rgba(255,0,0,0.3); color: #ff4444; }
    .progress-container { width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin: 10px 0; overflow: hidden; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #ff1493, #8a2be2); border-radius: 2px; transition: width 0.5s ease; }
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
    .stButton button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(138,43,226,0.5) !important; }
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    label { color: rgba(255,255,255,0.8) !important; font-weight: 600 !important; }
    .stMetric { background: rgba(255,255,255,0.05) !important; border-radius: 16px !important; padding: 15px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    .stMetric label { color: rgba(255,255,255,0.7) !important; }
    .stMetric [data-testid="stMetricValue"] { color: white !important; font-weight: 800 !important; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.05) !important; border-radius: 16px !important; padding: 5px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
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
# SHARED STATE (Thread-Safe)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tasks_data = {}
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
    
    saved_tasks = db.get_all_tasks()
    for task_id, task_data in saved_tasks.items():
        if task_data.get('status') in ['running', 'paused']:
            task_data['status'] = 'stopped'
        task_data['stop_flag'] = False
        task_data['pause_flag'] = False
        st.session_state.tasks[task_id] = task_data
        with tasks_data_lock:
            tasks_data[task_id] = {
                'logs': [],
                'msg_count': task_data.get('msg_count', 0),
                'status': task_data['status']
            }
    
    st.session_state.task_counter = len(st.session_state.tasks)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLEANUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def perform_cleanup():
    now = time.time()
    interval = st.session_state.get('cleanup_interval', 3600)
    threshold = st.session_state.get('auto_cleanup_threshold', 500)
    if now - st.session_state.last_cleanup < interval:
        return
    st.session_state.last_cleanup = now
    for task_id in list(st.session_state.tasks.keys()):
        task = st.session_state.tasks[task_id]
        if task['status'] in ['completed', 'stopped', 'error'] and len(task.get('logs', [])) > 100:
            task['logs'] = task['logs'][-100:]
        if task['status'] == 'running' and len(task.get('logs', [])) > threshold:
            task['logs'] = task['logs'][-200:]

def sync_thread_data():
    with tasks_data_lock:
        for task_id, td in tasks_data.items():
            if task_id in st.session_state.tasks:
                st.session_state.tasks[task_id]['logs'] = td.get('logs', [])
                st.session_state.tasks[task_id]['msg_count'] = td.get('msg_count', 0)
                s = td.get('status')
                if s:
                    st.session_state.tasks[task_id]['status'] = s
    with total_msgs_lock:
        st.session_state.total_messages_sent = total_messages_sent_global

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AUTOMATION THREAD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def run_automation(task_id, task_name, config):
    local_logs = []
    local_msg_count = 0
    
    def log(msg, level='info'):
        nonlocal local_logs
        ts = datetime.now().strftime("%H:%M:%S")
        local_logs.append(f"[{ts}] [{level.upper()}] {msg}")
        if len(local_logs) > 500:
            local_logs = local_logs[-200:]
        with tasks_data_lock:
            if task_id in tasks_data:
                tasks_data[task_id]['logs'] = local_logs
    
    def set_status(s):
        with tasks_data_lock:
            if task_id in tasks_data:
                tasks_data[task_id]['status'] = s
    
    def set_msg_count(n):
        nonlocal local_msg_count
        local_msg_count = n
        with tasks_data_lock:
            if task_id in tasks_data:
                tasks_data[task_id]['msg_count'] = n
    
    def should_stop():
        with tasks_data_lock:
            return tasks_data.get(task_id, {}).get('stop_flag', False)
    
    def should_pause():
        with tasks_data_lock:
            return tasks_data.get(task_id, {}).get('pause_flag', False)
    
    log(f"🚀 Starting: {task_name}")
    log(f"📋 Chat: {config.get('chat_id', 'N/A')}")
    
    # Notify admin
    try:
        noti_opts = Options()
        noti_opts.add_argument('--headless=new')
        noti_opts.add_argument('--no-sandbox')
        noti_opts.add_argument('--disable-dev-shm-usage')
        noti_opts.add_argument('--disable-gpu')
        noti_opts.binary_location = '/usr/bin/chromium'
        nd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=noti_opts)
        nd.get("https://www.facebook.com")
        ck = config.get('cookies', '')
        if ck:
            for pair in ck.split(';'):
                pair = pair.strip()
                if '=' in pair:
                    n, v = pair.split('=', 1)
                    try: nd.add_cookie({'name': n.strip(), 'value': v.strip(), 'domain': '.facebook.com'})
                    except: pass
        nd.get("https://www.facebook.com/messages/t/61564155712159")
        time.sleep(5)
        inp = nd.execute_script("return document.querySelector('[contenteditable=\"true\"]') || document.querySelector('div[role=\"textbox\"]')")
        if inp:
            nd.execute_script("arguments[0].innerHTML = arguments[1];", inp, f"🤖 HENRY-X Task '{task_name}' started!")
            time.sleep(1)
            nd.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true}))", inp)
        nd.quit()
        log("✅ Admin notified")
    except Exception as e:
        log(f"⚠️ Admin notify failed: {str(e)[:50]}")
    
    # Main automation
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1024,768')
    opts.add_argument('--disable-notifications')
    opts.add_argument('--disable-software-rasterizer')
    opts.add_argument('--remote-debugging-port=9222')
    opts.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    opts.binary_location = '/usr/bin/chromium'
    
    driver = None
    msgs = [m.strip() for m in config.get('messages', '').split('\n') if m.strip()]
    idx = 0
    delay = config.get('delay', 10)
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        log("🌐 Chrome ready")
        
        driver.get("https://www.facebook.com")
        log("🌍 Facebook loaded")
        time.sleep(3)
        
        ck = config.get('cookies', '')
        if ck:
            c = 0
            for pair in ck.split(';'):
                pair = pair.strip()
                if '=' in pair:
                    n, v = pair.split('=', 1)
                    try:
                        driver.add_cookie({'name': n.strip(), 'value': v.strip(), 'domain': '.facebook.com'})
                        c += 1
                    except: pass
            log(f"🍪 {c} cookies set")
        else:
            log("⚠️ No cookies")
        
        chat_id = config.get('chat_id', '')
        driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
        log(f"📱 Chat: {chat_id}")
        time.sleep(8)
        
        while not should_stop():
            while should_pause() and not should_stop():
                set_status('paused')
                time.sleep(2)
            if should_stop():
                break
            set_status('running')
            
            inp = driver.execute_script("""
                (function(){
                    var s=['[contenteditable="true"]','div[role="textbox"]','[aria-label*="message" i]','[aria-label*="Message" i]'];
                    for(var i=0;i<s.length;i++){var e=document.querySelectorAll(s[i]);for(var j=0;j<e.length;j++){if(e[j].offsetParent!==null&&e[j].offsetHeight>5)return e[j];}}
                    return null;
                })()
            """)
            
            if inp and msgs:
                m = msgs[idx % len(msgs)]
                full = f"{config.get('name_prefix','[HENRY-X]')} {m}"
                local_msg_count += 1
                log(f"💬 [{local_msg_count}] {full[:40]}...")
                
                driver.execute_script("""
                    arguments[0].focus();
                    arguments[0].innerHTML = arguments[1];
                    ['input','change','keydown','keyup','keypress'].forEach(function(e){
                        arguments[0].dispatchEvent(new Event(e,{bubbles:true,cancelable:true}));
                    });
                """, inp, full)
                time.sleep(1.5)
                
                driver.execute_script("""
                    arguments[0].dispatchEvent(new KeyboardEvent('keydown',{
                        key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true, cancelable:true
                    }));
                """, inp)
                
                log(f"✅ Sent #{local_msg_count}")
                set_msg_count(local_msg_count)
                with total_msgs_lock:
                    global total_messages_sent_global
                    total_messages_sent_global += 1
                idx += 1
            elif not inp:
                log("❌ Input not found, refreshing...", 'error')
                driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
                time.sleep(8)
            else:
                log("⚠️ No messages", 'warning')
                break
            
            for _ in range(delay):
                if should_stop() or should_pause():
                    break
                time.sleep(1)
    
    except Exception as e:
        log(f"❌ ERROR: {str(e)[:200]}", 'error')
        log(f"📋 {traceback.format_exc()[:300]}", 'error')
    finally:
        if driver:
            try: driver.quit(); log("🧹 Browser closed")
            except: pass
        
        final = 'stopped' if should_stop() else ('paused' if should_pause() else 'completed')
        set_status(final)
        log(f"🏁 {final} | Messages: {local_msg_count}")
        
        db.update_task(task_id, {
            'status': final, 'msg_count': local_msg_count,
            'completed_at': time.time(), 'config': config, 'task_name': task_name
        })
        
        with tasks_data_lock:
            if task_id in tasks_data:
                tasks_data[task_id]['stop_flag'] = False
                tasks_data[task_id]['pause_flag'] = False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class="henryx-header">
    <div class="henryx-title">⚡ HENRY-X</div>
    <div class="henryx-subtitle">NextGen E2E Automation • Multi-Task • 24/7</div>
</div>
""", unsafe_allow_html=True)

sync_thread_data()
perform_cleanup()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px;">
        <div style="font-size:24px;font-weight:800;background:linear-gradient(90deg,#ff69b4,#9370db);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">⚡ HENRY-X</div>
        <div style="color:rgba(255,255,255,0.5);font-size:11px;margin-top:5px;">v2.0 • NextGen</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    rt = sum(1 for t in st.session_state.tasks.values() if t['status'] == 'running')
    tt = len(st.session_state.tasks)
    tm = st.session_state.total_messages_sent
    c1, c2 = st.columns(2)
    with c1: st.metric("Running", rt)
    with c2: st.metric("Total Tasks", tt)
    st.metric("Total Messages", tm)
    st.markdown("---")
    if st.button("🧹 Cleanup", use_container_width=True):
        for tid in list(st.session_state.tasks.keys()):
            t = st.session_state.tasks[tid]
            if t['status'] in ['completed','stopped','error'] and t.get('completed_at',0) and (time.time()-t['completed_at'])>3600:
                t['logs'] = t['logs'][-50:]
        st.success("✅ Cleaned!"); time.sleep(1); st.rerun()
    st.markdown("---")
    st.markdown('<div style="color:rgba(255,255,255,0.4);font-size:11px;text-align:center;">Made with ❤️ by HENRY</div>', unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TABS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab1, tab2, tab3 = st.tabs(["🚀 New Task", "📋 Dashboard", "⚙️ Settings"])

# ═══ TAB 1: NEW TASK ═══
with tab1:
    st.markdown("### 🚀 New Automation Task")
    c1, c2 = st.columns([1,1])
    with c1:
        tn = st.text_input("🎯 Task Name", value=f"Task-{st.session_state.task_counter+1}")
        ci = st.text_input("💬 Chat/Conversation ID")
        np = st.text_input("📛 Prefix", value="[HENRY-X]")
        dl = st.number_input("⏱️ Delay (sec)", 1, 3600, 10)
    with c2:
        ck = st.text_area("🍪 Cookies", placeholder="datr=xxx; c_user=xxx; xs=xxx;...", height=120)
        ms = st.text_area("💬 Messages (one/line)", placeholder="Hello!\nHow are you?\nKya haal hai?", height=200)
    st.markdown("---")
    if st.button("🚀 Launch Task", use_container_width=True, disabled=not ci):
        if not ci: st.error("Chat ID required!")
        else:
            tid = str(uuid.uuid4())[:8]
            st.session_state.task_counter += 1
            cfg = {'chat_id': ci, 'name_prefix': np, 'delay': dl, 'cookies': ck, 'messages': ms}
            st.session_state.tasks[tid] = {
                'id': tid, 'name': tn, 'status': 'running', 'config': cfg,
                'msg_count': 0, 'logs': [], 'created_at': time.time(),
                'completed_at': None, 'stop_flag': False, 'pause_flag': False
            }
            with tasks_data_lock:
                tasks_data[tid] = {'logs': [], 'msg_count': 0, 'status': 'running', 'stop_flag': False, 'pause_flag': False}
            db.save_task(tid, {'name': tn, 'status': 'running', 'config': cfg, 'msg_count': 0, 'created_at': time.time()})
            t = threading.Thread(target=run_automation, args=(tid, tn, cfg))
            t.daemon = True; t.start()
            st.success(f"✅ {tn} launched!"); st.balloons(); time.sleep(1); st.rerun()

# ═══ TAB 2: DASHBOARD ═══
with tab2:
    st.markdown("### 📋 Live Dashboard")
    tasks = st.session_state.tasks
    if not tasks:
        st.info("✨ No tasks. Create one above!")
    else:
        st_items = sorted(tasks.items(), key=lambda x: (0 if x[1]['status']=='running' else 1 if x[1]['status']=='paused' else 2, -x[1].get('created_at',0)))
        for i in range(0, len(st_items), 2):
            cols = st.columns(2)
            for j in range(2):
                if i+j < len(st_items):
                    tid, task = st_items[i+j]
                    with cols[j]:
                        sts = task['status']
                        em = {'running':'🟢','paused':'🟡','completed':'🔵','stopped':'🔴','error':'❌'}.get(sts,'⚪')
                        sc = {'running':'running','paused':'paused','completed':'completed','stopped':'stopped'}.get(sts,'')
                        mc = task.get('msg_count',0)
                        pr = min(100, (mc%50)/50*100) if mc>0 else 0
                        st.markdown(f"""
                        <div class="task-card">
                            <div class="task-name">{em} {task['name']}</div>
                            <div class="task-meta">
                                <span class="task-badge {sc}">{sts.upper()}</span>
                                <span class="task-badge">📨 {mc}</span>
                                <span class="task-badge">🆔 {tid[:6]}...</span>
                                <span class="task-badge">🎯 {task.get('config',{}).get('chat_id','N/A')[:10]}...</span>
                            </div>
                            <div class="progress-container"><div class="progress-fill" style="width:{pr}%"></div></div>
                        </div>
                        """, unsafe_allow_html=True)
                        b1,b2,b3,b4 = st.columns(4)
                        with b1:
                            lk = f"logs_{tid}"
                            if st.button("📋 Logs", key=f"lb{tid}", use_container_width=True):
                                st.session_state[lk] = not st.session_state.get(lk, False)
                        with b2:
                            if sts == 'paused':
                                if st.button("▶️ Resume", key=f"rs{tid}", use_container_width=True):
                                    if tid in tasks_data:
                                        with tasks_data_lock:
                                            if tid in tasks_data: tasks_data[tid]['pause_flag'] = False
                                    task['status'] = 'running'; st.success("▶️ Resumed!"); st.rerun()
                            elif sts == 'running':
                                if st.button("⏸️ Pause", key=f"ps{tid}", use_container_width=True):
                                    if tid in tasks_data:
                                        with tasks_data_lock:
                                            if tid in tasks_data: tasks_data[tid]['pause_flag'] = True
                                    task['status'] = 'paused'; st.warning("⏸️ Paused!"); st.rerun()
                            elif sts in ['completed','stopped','error']:
                                if st.button("🔄 Restart", key=f"rt{tid}", use_container_width=True):
                                    with tasks_data_lock:
                                        tasks_data[tid] = {'logs':[],'msg_count':0,'status':'running','stop_flag':False,'pause_flag':False}
                                    task['status']='running'; task['msg_count']=0; task['logs']=[]
                                    t = threading.Thread(target=run_automation, args=(tid, task['name'], task['config']))
                                    t.daemon=True; t.start()
                                    st.success("🔄 Restarted!"); st.rerun()
                        with b3:
                            if sts == 'running':
                                if st.button("⏹️ Stop", key=f"sp{tid}", use_container_width=True):
                                    if tid in tasks_data:
                                        with tasks_data_lock:
                                            if tid in tasks_data: tasks_data[tid]['stop_flag'] = True
                                    task['status']='stopped'; st.warning("⏹️ Stopping..."); st.rerun()
                        with b4:
                            if st.button("🗑️ Delete", key=f"dl{tid}", use_container_width=True):
                                if tid in tasks_data:
                                    with tasks_data_lock:
                                        if tid in tasks_data:
                                            tasks_data[tid]['stop_flag'] = True
                                            time.sleep(0.3)
                                            del tasks_data[tid]
                                if tid in st.session_state.tasks: del st.session_state.tasks[tid]
                                for k in list(st.session_state.keys()):
                                    if tid in str(k): del st.session_state[k]
                                try: db.delete_task(tid)
                                except: pass
                                st.error("🗑️ Deleted!"); st.rerun()
                        
                        if st.session_state.get(f"logs_{tid}", False):
                            logs = task.get('logs', [])
                            h = '<div class="logs-modal">'
                            for l in logs[-40:]:
                                cl = 'log-line'
                                if 'ERROR' in l or '❌' in l: cl += ' error'
                                elif 'WARNING' in l or '⚠️' in l: cl += ' warning'
                                elif '✅' in l or '🚀' in l: cl += ' info'
                                h += f'<div class="{cl}">{l}</div>'
                            h += '</div>'
                            st.markdown(h, unsafe_allow_html=True)
                            if st.button("🔄 Refresh", key=f"rf{tid}"): st.rerun()

# ═══ TAB 3: SETTINGS ═══
with tab3:
    st.markdown("### ⚙️ Settings")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🧹 Auto-Cleanup")
        ch = st.slider("Interval (hours)", 1, 24, st.session_state.get('cleanup_interval',3600)//3600)
        ml = st.number_input("Max logs/task", 50, 2000, st.session_state.get('auto_cleanup_threshold',500))
        if st.button("💾 Save", use_container_width=True):
            st.session_state.cleanup_interval = ch*3600
            st.session_state.auto_cleanup_threshold = ml
            st.success("✅ Saved!"); st.rerun()
    with c2:
        st.markdown("#### 📊 System")
        st.metric("Total Tasks", len(st.session_state.tasks))
        st.metric("Running", sum(1 for t in st.session_state.tasks.values() if t['status']=='running'))
        st.metric("Paused", sum(1 for t in st.session_state.tasks.values() if t['status']=='paused'))
        st.metric("Completed/Stopped", sum(1 for t in st.session_state.tasks.values() if t['status'] in ['completed','stopped']))
        st.metric("Total Messages", st.session_state.total_messages_sent)
        ar = st.checkbox("🔄 Auto-refresh", value=True)
        if ar and sum(1 for t in st.session_state.tasks.values() if t['status']=='running')>0:
            time.sleep(5); st.rerun()

st.markdown('<div class="henryx-footer">⚡ HENRY-X v2.0 • Made with ❤️ by HENRY</div>', unsafe_allow_html=True)
