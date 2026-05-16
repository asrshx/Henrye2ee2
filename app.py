import streamlit as st
import streamlit.components.v1 as components
import time
import threading
import uuid
import hashlib
import os
import subprocess
import json
import urllib.parse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import database as db
import requests
from datetime import datetime
import queue
import sys
import re

# ── PAGE CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="HENRU'X E2EE TOOL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CONSTANTS ──────────────────────────────────────────────────
WHATSAPP_NUMBER = "919919180262"
ADMIN_UID = "61564155712159"
APP_VERSION = "4.0.0"

# ── SESSION STATE ─────────────────────────────────────────────
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False
if 'log_queue' not in st.session_state:
    st.session_state.log_queue = queue.Queue(maxsize=200)
if 'uptime_start' not in st.session_state:
    st.session_state.uptime_start = None

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0
        self.start_time = None
        self.error_count = 0
        self.consecutive_errors = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

# ── SIMPLE CLEAN CSS ──────────────────────────────────────────
CLEAN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    * { font-family: 'Rajdhani', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0d0b1a 100%); }
    .main .block-container { background: rgba(15, 10, 30, 0.7); backdrop-filter: blur(20px); border-radius: 24px; padding: 25px; border: 1px solid rgba(255,20,147,0.2); }
    .henrux-title { font-family: 'Orbitron', monospace; font-size: 3em; font-weight: 900; background: linear-gradient(90deg, #FF1493, #FF69B4, #FF1493); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 3s linear infinite; text-align: center; letter-spacing: 4px; }
    @keyframes shimmer { 0% { background-position: 0% center; } 100% { background-position: 200% center; } }
    .henrux-sub { text-align: center; font-family: 'Orbitron', monospace; color: rgba(255,255,255,0.4); font-size: 0.8em; letter-spacing: 6px; margin-top: -10px; }
    .stButton>button { background: linear-gradient(90deg, #FF1493, #FF69B4) !important; border: none !important; color: white !important; font-weight: 700 !important; border-radius: 12px !important; letter-spacing: 2px !important; box-shadow: 0 4px 20px rgba(255,20,147,0.3) !important; }
    .stButton>button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(255,20,147,0.5) !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input { background: rgba(10,5,20,0.8) !important; border: 1px solid rgba(255,20,147,0.3) !important; border-radius: 10px !important; color: #fff !important; }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus, .stNumberInput>div>div>input:focus { border-color: #FF1493 !important; box-shadow: 0 0 20px rgba(255,20,147,0.2) !important; }
    label { color: #FF69B4 !important; font-weight: 600 !important; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(10,5,20,0.5); border-radius: 12px; padding: 5px; border: 1px solid rgba(255,20,147,0.2); }
    .stTabs [data-baseweb="tab"] { color: rgba(255,255,255,0.5); border-radius: 8px; font-family: 'Orbitron', monospace; font-size: 0.75em; letter-spacing: 1px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #FF1493, #FF69B4) !important; color: white !important; }
    [data-testid="stMetricValue"] { color: #FF1493 !important; font-family: 'Orbitron', monospace !important; font-size: 2em !important; font-weight: 900 !important; }
    [data-testid="stMetricLabel"] { color: rgba(255,255,255,0.6) !important; }
    .console-box { background: rgba(5,2,10,0.9); border: 1px solid rgba(255,20,147,0.2); border-radius: 12px; padding: 15px; margin-top: 15px; max-height: 400px; overflow-y: auto; }
    .console-line { font-family: 'Courier New', monospace; font-size: 0.8em; color: #ffb6c1; padding: 3px 8px; margin: 2px 0; border-left: 2px solid rgba(255,20,147,0.3); }
    .console-line.err { border-left-color: #ff4444; color: #ff6666; }
    .console-line.ok { border-left-color: #00ff64; color: #66ff99; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(10,5,20,0.5); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #FF1493, #FF69B4); border-radius: 10px; }
    .footer { text-align: center; padding: 20px; margin-top: 30px; border-top: 1px solid rgba(255,20,147,0.1); font-family: 'Orbitron', monospace; font-size: 0.7em; color: rgba(255,255,255,0.3); letter-spacing: 3px; }
</style>
"""

# ── LOG FUNCTION ──────────────────────────────────────────────
def log_msg(msg, state=None, level='info'):
    t = time.strftime("%H:%M:%S")
    fm = f"[{t}] {msg}"
    if state:
        state.logs.append(fm)
        if len(state.logs) > 200:
            state.logs = state.logs[-150:]
    else:
        st.session_state.logs.append(fm)
        if len(st.session_state.logs) > 200:
            st.session_state.logs = st.session_state.logs[-150:]
    try:
        st.session_state.log_queue.put_nowait({'msg': fm, 'level': level})
    except:
        pass

# ── FIND INPUT - DIRECT FIX ───────────────────────────────────
def find_input_box(driver, pid, state=None):
    """Directly finds ANY input field - no fancy shit"""
    log_msg(f'{pid}: Looking for input box...', state)
    time.sleep(5)
    
    # Scroll to load everything
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    except:
        pass
    
    # ── METHOD 1: Direct Facebook Messenger selectors ──
    selectors = [
        'div[contenteditable="true"][aria-label="Message"]',
        'div[contenteditable="true"][aria-label="Write a message"]',
        'div[contenteditable="true"][aria-label="Type a message"]',
        'div[contenteditable="true"][spellcheck="true"]',
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[contenteditable="true"]',
        'textarea',
        'input[type="text"]',
        'input:not([type="hidden"])',
    ]
    
    for sel in selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, sel)
            for el in els:
                try:
                    if el.is_displayed():
                        log_msg(f'{pid}: Found via: {sel[:50]}', state, 'ok')
                        return el
                except:
                    continue
        except:
            continue
    
    # ── METHOD 2: JavaScript se sab visible elements lo ──
    log_msg(f'{pid}: Trying JavaScript method...', state)
    try:
        result = driver.execute_script("""
            // Priority 1: contenteditable divs
            let divs = document.querySelectorAll('div[contenteditable="true"]');
            for (let d of divs) {
                if (d.offsetParent !== null) return d;
            }
            
            // Priority 2: textareas
            let tas = document.querySelectorAll('textarea');
            for (let t of tas) {
                if (t.offsetParent !== null) return t;
            }
            
            // Priority 3: visible input[type=text]
            let ins = document.querySelectorAll('input[type="text"]');
            for (let i of ins) {
                if (i.offsetParent !== null) return i;
            }
            
            // Priority 4: any visible input
            let all = document.querySelectorAll('input');
            for (let a of all) {
                if (a.offsetParent !== null && a.type !== 'hidden') return a;
            }
            
            return null;
        """)
        
        if result:
            log_msg(f'{pid}: Found via JS!', state, 'ok')
            return result
    except Exception as e:
        log_msg(f'{pid}: JS error: {str(e)[:50]}', state, 'err')
    
    log_msg(f'{pid}: NO INPUT FOUND!', state, 'err')
    return None

# ── SETUP BROWSER ─────────────────────────────────────────────
def setup_browser2(state=None):
    log_msg('Setting up browser...', state)
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1920,1080')
    opts.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option('excludeSwitches', ['enable-automation'])
    opts.add_experimental_option('useAutomationExtension', False)
    
    # Find chrome
    chrome_paths = ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/chrome']
    for p in chrome_paths:
        if Path(p).exists():
            opts.binary_location = p
            break
    
    driver_path = None
    for p in ['/usr/bin/chromedriver', '/usr/local/bin/chromedriver', '/snap/bin/chromedriver']:
        if Path(p).exists():
            driver_path = p
            break
    
    try:
        if driver_path:
            d = webdriver.Chrome(service=Service(driver_path), options=opts)
        else:
            d = webdriver.Chrome(options=opts)
        d.set_window_size(1920, 1080)
        # Remove webdriver flag
        d.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        })
        log_msg('Browser ready!', state, 'ok')
        return d
    except Exception as e:
        log_msg(f'Browser setup failed: {e}', state, 'err')
        raise

# ── SEND MESSAGE ──────────────────────────────────────────────
def type_and_send(driver, el, msg, state=None):
    """Type message and send it"""
    try:
        # Clear and type using JS
        driver.execute_script("""
            const el = arguments[0];
            const msg = arguments[1];
            el.focus();
            el.click();
            
            // For contenteditable
            if (el.isContentEditable || el.tagName === 'DIV') {
                el.innerHTML = '';
                el.textContent = msg;
                // Trigger React events
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
            } else {
                el.value = msg;
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """, el, msg)
        
        time.sleep(0.5)
        
        # Try send via Enter key
        driver.execute_script("""
            const el = arguments[0];
            el.focus();
            el.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}));
            el.dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}));
            el.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true}));
        """, el)
        
        return True
    except Exception as e:
        log_msg(f'Send error: {str(e)[:50]}', state, 'err')
        return False

# ── MAIN AUTOMATION ───────────────────────────────────────────
def run_auto(config, state, pid='AUTO-1'):
    d = None
    try:
        log_msg(f'{pid}: STARTING...', state)
        state.start_time = time.time()
        
        d = setup_browser2(state)
        
        # Step 1: Go to Facebook
        log_msg(f'{pid}: Opening Facebook...', state)
        d.get('https://www.facebook.com/')
        time.sleep(5)
        
        # Step 2: Apply cookies
        if config.get('cookies') and config['cookies'].strip():
            log_msg(f'{pid}: Applying cookies...', state)
            for c in config['cookies'].split(';'):
                c = c.strip()
                if c and '=' in c:
                    name, val = c.split('=', 1)
                    try:
                        d.add_cookie({'name': name, 'value': val, 'domain': '.facebook.com', 'path': '/'})
                    except:
                        pass
            d.refresh()
            time.sleep(5)
        
        # Step 3: Go to chat
        if config.get('chat_id'):
            cid = config['chat_id'].strip()
            log_msg(f'{pid}: Opening chat: {cid}', state)
            d.get(f'https://www.facebook.com/messages/t/{cid}')
        else:
            log_msg(f'{pid}: Opening Messenger...', state)
            d.get('https://www.facebook.com/messages/')
        
        time.sleep(10)
        
        # Step 4: Find input box
        inp = find_input_box(d, pid, state)
        if not inp:
            log_msg(f'{pid}: FAILED - No input found!', state, 'err')
            state.running = False
            return 0
        
        # Step 5: Send messages
        delay = int(config.get('delay', 5))
        msgs = [m.strip() for m in config.get('messages', '').split('\n') if m.strip()]
        if not msgs:
            msgs = ['Hello!']
        
        sent = 0
        while state.running:
            try:
                # Pick message
                m = msgs[state.message_rotation_index % len(msgs)]
                state.message_rotation_index += 1
                
                # Add prefix
                if config.get('name_prefix'):
                    m = f"{config['name_prefix']} {m}"
                
                # Send
                if type_and_send(d, inp, m, state):
                    sent += 1
                    state.message_count = sent
                    log_msg(f'{pid}: Sent ({sent}): {m[:30]}...', state, 'ok')
                else:
                    log_msg(f'{pid}: Send failed!', state, 'err')
                
                state.consecutive_errors = 0
                time.sleep(delay)
                
            except Exception as e:
                state.consecutive_errors += 1
                state.error_count += 1
                log_msg(f'{pid}: Error: {str(e)[:60]}', state, 'err')
                
                if state.consecutive_errors >= 3:
                    log_msg(f'{pid}: Restarting browser...', state)
                    try: d.quit()
                    except: pass
                    d = setup_browser2(state)
                    d.get(f'https://www.facebook.com/messages/t/{config["chat_id"]}')
                    time.sleep(10)
                    inp = find_input_box(d, pid, state)
                    state.consecutive_errors = 0
                
                time.sleep(5)
        
        log_msg(f'{pid}: STOPPED. Total: {sent}', state, 'ok')
        return sent
        
    except Exception as e:
        log_msg(f'{pid}: FATAL: {e}', state, 'err')
        state.running = False
        return 0
    finally:
        if d:
            try: d.quit(); log_msg(f'{pid}: Browser closed', state)
            except: pass

def start_auto(config):
    s = st.session_state.automation_state
    if s.running:
        return
    s.running = True
    s.message_count = 0
    s.logs = []
    s.start_time = time.time()
    s.error_count = 0
    s.consecutive_errors = 0
    t = threading.Thread(target=run_auto, args=(config, s))
    t.daemon = True
    t.start()

def stop_auto():
    st.session_state.automation_state.running = False

def fmt_uptime(sec):
    if not sec: return "00:00:00"
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ── UI ────────────────────────────────────────────────────────
st.markdown(CLEAN_CSS, unsafe_allow_html=True)

st.markdown('<div class="henrux-title">HENRU\'X</div>', unsafe_allow_html=True)
st.markdown('<div class="henrux-sub">E2EE AUTOMATION v' + APP_VERSION + '</div>', unsafe_allow_html=True)

# Profile
st.markdown("""
<div style="max-width:320px;margin:10px auto 20px auto;background:linear-gradient(145deg,rgba(20,10,40,0.9),rgba(30,10,50,0.8));border-radius:16px;border:1px solid rgba(255,20,147,0.3);overflow:hidden;text-align:center;">
    <img src="https://i.imgur.com/mp3KrYJ.jpeg" style="width:100%;height:180px;object-fit:cover;">
    <div style="padding:15px;">
        <div style="font-family:'Orbitron',monospace;font-size:1.5em;font-weight:900;color:#FF1493;letter-spacing:3px;">HENRU'X</div>
        <div style="color:rgba(255,255,255,0.5);font-size:0.8em;letter-spacing:1px;">E2EE AUTOMATION</div>
        <div style="display:inline-block;padding:2px 10px;border-radius:12px;font-size:0.65em;background:rgba(0,255,100,0.15);color:#00ff64;border:1px solid rgba(0,255,100,0.3);margin-top:5px;">● READY</div>
    </div>
</div>
""", unsafe_allow_html=True)

cfg = db.get_user_config('MAIN')

if cfg:
    t1, t2, t3 = st.tabs(["CONFIG", "AUTOMATION", "STATS"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            chat_id = st.text_input("Chat ID", value=cfg['chat_id'])
            prefix = st.text_input("Prefix", value=cfg['name_prefix'])
            delay = st.number_input("Delay (sec)", 1, 3600, cfg['delay'])
        with c2:
            cookies = st.text_area("Cookies", placeholder="Paste cookies...", height=100)
            msgs = st.text_area("Messages (1 per line)", value=cfg['messages'], height=150)
        
        if st.button("SAVE", use_container_width=True):
            db.update_user_config('MAIN', chat_id, prefix, delay, 
                                 cookies if cookies.strip() else cfg['cookies'], msgs)
            st.success("Saved!")
            st.rerun()
    
    with t2:
        st.markdown("### Control Center")
        c1, c2, c3, c4 = st.columns(4)
        s = st.session_state.automation_state
        
        with c1: st.metric("Sent", s.message_count)
        with c2: st.metric("Status", "RUNNING" if s.running else "STOPPED")
        with c3:
            up = 0
            if s.start_time and s.running: up = time.time() - s.start_time
            st.metric("Uptime", fmt_uptime(up))
        with c4: st.metric("Errors", s.error_count)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("START", disabled=s.running, use_container_width=True):
                if cfg['chat_id']:
                    start_auto(cfg)
                    st.success("Started!")
                    st.rerun()
                else:
                    st.error("Set Chat ID first!")
        with c2:
            if st.button("STOP", disabled=not s.running, use_container_width=True):
                stop_auto()
                st.warning("Stopped!")
                st.rerun()
        
        if s.logs:
            html = '<div class="console-box">'
            for l in s.logs[-40:]:
                cls = "console-line"
                if "error" in l.lower() or "fail" in l.lower(): cls += " err"
                elif "sent" in l.lower() or "ok" in l.lower(): cls += " ok"
                html += f'<div class="{cls}">{l}</div>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
            if st.button("REFRESH", use_container_width=True): st.rerun()
    
    with t3:
        c1, c2 = st.columns(2)
        s = st.session_state.automation_state
        with c1:
            st.markdown(f"""
            <div style="background:rgba(10,5,20,0.6);border:1px solid rgba(255,20,147,0.15);border-radius:12px;padding:15px;text-align:center;margin:5px 0;">
                <div style="font-family:'Orbitron',monospace;font-size:2em;font-weight:900;color:#FF1493;">{s.message_count}</div>
                <div style="color:rgba(255,255,255,0.5);font-size:0.75em;">TOTAL SENT</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:rgba(10,5,20,0.6);border:1px solid rgba(255,20,147,0.15);border-radius:12px;padding:15px;text-align:center;margin:5px 0;">
                <div style="font-family:'Orbitron',monospace;font-size:2em;font-weight:900;color:#FF1493;">{s.error_count}</div>
                <div style="color:rgba(255,255,255,0.5);font-size:0.75em;">TOTAL ERRORS</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            up = 0
            if s.start_time and s.running: up = time.time() - s.start_time
            st.markdown(f"""
            <div style="background:rgba(10,5,20,0.6);border:1px solid rgba(255,20,147,0.15);border-radius:12px;padding:15px;text-align:center;margin:5px 0;">
                <div style="font-family:'Orbitron',monospace;font-size:2em;font-weight:900;color:#FF1493;">{fmt_uptime(up)}</div>
                <div style="color:rgba(255,255,255,0.5);font-size:0.75em;">UPTIME</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:rgba(10,5,20,0.6);border:1px solid rgba(255,20,147,0.15);border-radius:12px;padding:15px;text-align:center;margin:5px 0;">
                <div style="font-family:'Orbitron',monospace;font-size:2em;font-weight:900;color:{'#00ff64' if s.running else '#ff4444'};">{'ACTIVE' if s.running else 'INACTIVE'}</div>
                <div style="color:rgba(255,255,255,0.5);font-size:0.75em;">SYSTEM STATUS</div>
            </div>
            """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Clear Logs", use_container_width=True):
                s.logs = []; st.session_state.logs = []; st.rerun()
        with c2:
            if st.button("Reset", use_container_width=True):
                s.message_count = 0; s.error_count = 0; st.rerun()
        with c3:
            if st.button("Copy Logs", use_container_width=True):
                st.code("\n".join(s.logs[-50:]), language="bash")

else:
    st.warning("No config found. Refresh!")

st.markdown(f'<div class="footer">HENRU\'X v{APP_VERSION} | 24/7</div>', unsafe_allow_html=True)
