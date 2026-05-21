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
import database as db
import requests

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="HENRY'X - E2EE TOOL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CUSTOM CSS (NEON DARK THEME) ──
st.markdown("""
<style>
    /* Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: #0a0a12;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header */
    .header {
        text-align: center;
        padding: 30px 20px;
        margin-bottom: 30px;
        background: linear-gradient(135deg, rgba(255,20,147,0.08), rgba(139,0,255,0.08));
        border-radius: 20px;
        border: 1px solid rgba(139,0,255,0.15);
    }
    
    .header img {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 3px solid transparent;
        background: linear-gradient(135deg, #ff1493, #8b00ff, #00d4ff);
        padding: 3px;
        margin-bottom: 15px;
        box-shadow: 0 0 40px rgba(139,0,255,0.3);
    }
    
    .header h1 {
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(135deg, #ff1493, #8b00ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 3px;
    }
    
    .header p {
        color: #8888aa;
        font-size: 14px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 8px;
    }
    
    .header p span {
        color: #ff1493;
        font-weight: 700;
    }
    
    /* Cards */
    .card {
        background: #16162a;
        border: 1px solid #2a2a4a;
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        border-color: rgba(139,0,255,0.3);
        box-shadow: 0 0 30px rgba(139,0,255,0.08);
    }
    
    .card-title {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .card-title .icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #ff1493, #8b00ff);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #0f0f1a !important;
        border: 1px solid #2a2a4a !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
        font-size: 14px !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #8b00ff !important;
        box-shadow: 0 0 20px rgba(139,0,255,0.15) !important;
    }
    
    /* Labels */
    .stTextInput label, .stNumberInput label, .stTextArea label {
        color: #8888aa !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    
    /* Buttons */
    .stButton > button {
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #ff1493, #8b00ff) !important;
        color: white !important;
        box-shadow: 0 4px 25px rgba(139,0,255,0.25) !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 40px rgba(139,0,255,0.35) !important;
    }
    
    .stButton > button[data-testid="baseButton-secondary"] {
        background: transparent !important;
        border: 1px solid #2a2a4a !important;
        color: #8888aa !important;
    }
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        border-color: #8b00ff !important;
        color: #e0e0e0 !important;
    }
    
    /* Metrics */
    .stMetric {
        background: #0f0f1a;
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 15px;
    }
    
    .stMetric label {
        color: #8888aa !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ff1493, #8b00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #12121a;
        border-radius: 12px;
        padding: 5px;
        border: 1px solid #2a2a4a;
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #555577 !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #ff1493, #8b00ff) !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(139,0,255,0.3) !important;
    }
    
    /* Console */
    .console-output {
        background: #050510;
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        line-height: 1.8;
        max-height: 400px;
        overflow-y: auto;
        color: #8888aa;
    }
    
    .console-output .log-line {
        color: #8888aa;
    }
    
    .console-output .log-line::before {
        content: '> ';
        color: #8b00ff;
    }
    
    .console-output .log-line.info { color: #00d4ff; }
    .console-output .log-line.success { color: #00ff88; }
    .console-output .log-line.error { color: #ff3355; }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px !important;
    }
    
    .stAlert[data-testid="stAlert-success"] {
        background: rgba(0,204,102,0.1) !important;
        border: 1px solid #00cc66 !important;
    }
    
    .stAlert[data-testid="stAlert-error"] {
        background: rgba(255,51,85,0.1) !important;
        border: 1px solid #ff3355 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px;
        color: #555577;
        font-size: 13px;
        border-top: 1px solid #2a2a4a;
        margin-top: 40px;
    }
    
    .footer span {
        background: linear-gradient(135deg, #ff1493, #8b00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Info box */
    .info-box {
        background: rgba(139,0,255,0.08);
        border: 1px solid rgba(139,0,255,0.2);
        border-radius: 10px;
        padding: 15px;
        color: #8888aa;
        font-size: 13px;
        margin-bottom: 15px;
    }
    
    .info-box strong {
        color: #e0e0e0;
    }
    
    /* Cookie badge */
    .cookie-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        background: rgba(139,0,255,0.12);
        border: 1px solid rgba(139,0,255,0.25);
        border-radius: 8px;
        color: #b388ff;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header h1 { font-size: 32px; }
        .header img { width: 70px; height: 70px; }
    }
</style>
""", unsafe_allow_html=True)

# ── CONFIG ──
WHATSAPP_NUMBER = "919919180262"
ADMIN_UID = "100001493272464"

# ── SESSION STATE ──
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

if 'automation_state' not in st.session_state:
    st.session_state.automation_state = AutomationState()

# ── HELPER FUNCTIONS ──
def log_message(msg, automation_state=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    if automation_state:
        automation_state.logs.append(formatted_msg)
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(10)
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        selectors = [
            'div[contenteditable="true"][spellcheck="true"]',
            'div[role="textbox"]',
            'div[contenteditable="true"]',
            'textarea',
            'input[type="text"]',
            'input[type="search"]',
        ]
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                if el.is_displayed():
                    log_message(f'{process_id}: Found input via: {selector}', automation_state)
                    return el
        result = driver.execute_script("""
            const selectors = [
                'div[contenteditable="true"][spellcheck="true"]',
                'div[role="textbox"]',
                'div[contenteditable="true"]',
                'textarea',
                'input[type="text"]',
                'input[type="search"]'
            ];
            for (let sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.offsetParent !== null) return el;
            }
            const all = document.querySelectorAll('input, textarea, div[contenteditable]');
            for (let el of all) {
                if (el.offsetParent !== null) return el;
            }
            return null;
        """)
        if result:
            log_message(f'{process_id}: Found input via JS', automation_state)
            return driver.execute_script("return arguments[0];", result)
        log_message(f'{process_id}: No message input found', automation_state)
        return None
    except Exception as e:
        log_message(f'{process_id}: Error finding input: {str(e)}', automation_state)
        return None

def send_messages(user_config, automation_state, process_id='AUTO-1'):
    chat_id = user_config.get('chat_id', '')
    name_prefix = user_config.get('name_prefix', '[HENRYX]')
    delay = int(user_config.get('delay', 10))
    cookies_text = user_config.get('cookies', '')
    messages_text = user_config.get('messages', 'Hello')
    
    # Parse multi cookies
    cookie_sets = []
    if cookies_text and cookies_text.strip():
        for line in cookies_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'): continue
            cookie_sets.append(line)
    
    message_list = [m.strip() for m in messages_text.split('\n') if m.strip()]
    if not message_list:
        message_list = ["Hello"]
    
    log_message(f'{process_id}: Target: {chat_id} | Cookies: {len(cookie_sets)} | Messages: {len(message_list)}', automation_state)
    
    if not cookie_sets:
        cookie_sets = ['']
    
    cycle = 0
    while automation_state.running:
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            driver = webdriver.Chrome(options=chrome_options)
            
            log_message(f'{process_id}: Cycle {cycle+1} - Cookie set {(cycle % len(cookie_sets)) + 1}/{len(cookie_sets)}', automation_state)
            
            # Step 1: Load facebook.com first for domain
            driver.get("https://facebook.com")
            time.sleep(5)
            
            # Step 2: Apply cookies
            cookie_line = cookie_sets[cycle % len(cookie_sets)]
            if cookie_line:
                try:
                    if cookie_line.startswith('{'):
                        cookie_obj = json.loads(cookie_line)
                        driver.add_cookie(cookie_obj)
                    elif '=' in cookie_line:
                        name, value = cookie_line.split('=', 1)
                        driver.add_cookie({"name": name.strip(), "value": value.strip(), "domain": ".facebook.com", "path": "/"})
                except Exception as e:
                    log_message(f'{process_id}: Cookie error: {str(e)[:40]}', automation_state)
            
            # Step 3: Navigate to chat
            driver.get(f"https://www.facebook.com/messages/t/{chat_id}")
            time.sleep(10)
            
            # Find input
            msg_input = find_message_input(driver, process_id, automation_state)
            if not msg_input:
                log_message(f'{process_id}: Input not found - skipping cycle', automation_state)
                cycle += 1
                if driver: driver.quit()
                time.sleep(delay)
                continue
            
            log_message(f'{process_id}: Input found! Sending messages...', automation_state)
            
            for i in range(len(message_list)):
                if not automation_state.running: break
                
                idx = (automation_state.message_rotation_index + i) % len(message_list)
                message = message_list[idx]
                full_message = f"{name_prefix} {message}" if name_prefix else message
                
                try:
                    # Clear input
                    driver.execute_script("""
                        const el = arguments[0]; el.focus(); el.click();
                        if(el.tagName === 'DIV'){ el.textContent=''; el.innerHTML=''; }
                        else { el.value=''; }
                    """, msg_input)
                    time.sleep(0.3)
                    
                    # Type
                    for ch in full_message:
                        if not automation_state.running: break
                        driver.execute_script("""
                            const el=arguments[0], ch=arguments[1];
                            if(el.tagName==='DIV')el.textContent+=ch; else el.value+=ch;
                            el.dispatchEvent(new Event('input',{bubbles:true}));
                        """, msg_input, ch)
                        time.sleep(0.02)
                    
                    time.sleep(0.5)
                    
                    # Send
                    sent = driver.execute_script("""
                        const btns = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                        for(let b of btns){ const el=b.closest('button')||b; if(el.offsetParent!==null){el.click();return true;} }
                        return false;
                    """)
                    
                    if not sent:
                        driver.execute_script("""
                            const el=arguments[0];
                            el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',keyCode:13,bubbles:true}));
                            el.dispatchEvent(new KeyboardEvent('keyup',{key:'Enter',keyCode:13,bubbles:true}));
                        """, msg_input)
                    
                    automation_state.message_count += 1
                    st.session_state.message_count = automation_state.message_count
                    log_message(f'{process_id}: Sent ({automation_state.message_count})', automation_state)
                    
                    if automation_state.message_count % 30 == 0:
                        log_message(f'{process_id}: Cooldown 20s...', automation_state)
                        time.sleep(20)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    log_message(f'{process_id}: Send error: {str(e)[:40]}', automation_state)
            
            automation_state.message_rotation_index += len(message_list)
            log_message(f'{process_id}: Cycle {cycle+1} done. Waiting {delay}s...', automation_state)
            
        except Exception as e:
            log_message(f'{process_id}: Error: {str(e)[:50]}', automation_state)
        finally:
            if driver:
                try: driver.quit()
                except: pass
        
        if not automation_state.running: break
        cycle += 1
        time.sleep(delay)
    
    log_message(f'{process_id}: Stopped.', automation_state)

def send_admin_notification(user_config, process_id, automation_state):
    log_message(f"ADMIN-NOTIFY: Skipped (headless mode)", automation_state)

def run_automation_with_notification(user_config, automation_state, process_id='AUTO-1'):
    send_admin_notification(user_config, process_id, automation_state)
    send_messages(user_config, automation_state, process_id)

def start_automation(user_config):
    automation_state = st.session_state.automation_state
    if automation_state.running: return
    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    st.session_state.logs = []
    st.session_state.message_count = 0
    db.set_automation_running('MAIN', True)
    thread = threading.Thread(target=run_automation_with_notification, args=(user_config, automation_state))
    thread.daemon = True
    thread.start()

def stop_automation():
    st.session_state.automation_state.running = False
    db.set_automation_running('MAIN', False)

# ── HEADER ──
st.markdown("""
<div class="header">
    <img src="https://i.imgur.com/mp3KrYJ.jpeg" onerror="this.style.display='none'">
    <h1>HENRY'X</h1>
    <p>Offline <span>E2EE</span> Automation Tool</p>
</div>
""", unsafe_allow_html=True)

# ── GET CONFIG ──
user_config = db.get_user_config('MAIN')

if user_config:
    tab1, tab2, tab3 = st.tabs(["⚙ Configuration", "▶ Automation", "🍪 Multi-Cookies"])
    
    with tab1:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon">⚙</span> Tool Configuration</div>', unsafe_allow_html=True)
            
            chat_id = st.text_input("Chat / Conversation ID", value=user_config.get('chat_id', ''), placeholder="Enter Facebook Chat ID...", key="chat_id_input")
            
            col1, col2 = st.columns(2)
            with col1:
                name_prefix = st.text_input("Name Prefix", value=user_config.get('name_prefix', '[HENRYX]'), placeholder="[HENRYX]", key="prefix_input")
            with col2:
                delay = st.number_input("Delay (seconds)", min_value=1, value=int(user_config.get('delay', 10)), key="delay_input")
            
            messages = st.text_area("Messages (one per line)", value=user_config.get('messages', ''), height=150, key="msg_input")
            cookies_config = st.text_area("Cookies (optional - set in Multi-Cookies tab)", value="", height=80, key="cookies_config_input", disabled=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Save Configuration", type="primary", use_container_width=True):
                    final_cookies = user_config.get('cookies', '') if not cookies_config.strip() else cookies_config
                    db.update_user_config('MAIN', chat_id, name_prefix, delay, final_cookies, messages)
                    st.success("✅ Configuration saved!")
                    st.rerun()
            with col2:
                if st.button("🔄 Reload", type="secondary", use_container_width=True):
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon">▶</span> Automation Control</div>', unsafe_allow_html=True)
            
            auto_state = st.session_state.automation_state
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Messages Sent", auto_state.message_count)
            with col2:
                status = "Running" if auto_state.running else "Stopped"
                st.metric("Status", status)
            with col3:
                st.metric("Chat ID", user_config.get('chat_id', '')[:12] + "..." if user_config.get('chat_id') else "Not Set")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Start Automation", type="primary", disabled=auto_state.running, use_container_width=True):
                    if user_config.get('chat_id') and user_config['chat_id'] not in ['', 'Enter Your Chat Id']:
                        start_automation(user_config)
                        st.success("Automation started!")
                        st.rerun()
                    else:
                        st.error("Please set Chat ID in Configuration first!")
            with col2:
                if st.button("⏹ Stop Automation", type="secondary", disabled=not auto_state.running, use_container_width=True):
                    stop_automation()
                    st.warning("Automation stopped!")
                    st.rerun()
            
            # Console
            st.markdown("### Live Console")
            logs_to_show = auto_state.logs if auto_state.logs else st.session_state.logs
            if logs_to_show:
                logs_html = '<div class="console-output">'
                for log in logs_to_show[-40:]:
                    logs_html += f'<div class="log-line">{log}</div>'
                logs_html += '</div>'
                st.markdown(logs_html, unsafe_allow_html=True)
                
                if st.button("🔄 Refresh Logs", type="secondary"):
                    st.rerun()
            else:
                st.markdown('<div class="console-output"><div class="log-line">Ready. Configure and start automation.</div></div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon">🍪</span> Multi-Cookie Manager</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
                <strong>How it works:</strong> Paste one cookie per line. The tool will rotate through all cookie sets automatically.
                Each line can be JSON format (<code>{"name":"c_user","value":"123","domain":".facebook.com"}</code>) 
                or simple format (<code>c_user=12345</code>).
            </div>
            """, unsafe_allow_html=True)
            
            cookies_value = user_config.get('cookies', '')
            cookie_lines = [l for l in cookies_value.strip().split('\n') if l.strip()] if cookies_value else []
            
            if cookie_lines:
                st.markdown(f'<div class="cookie-badge">🍪 {len(cookie_lines)} cookie set(s) loaded</div>', unsafe_allow_html=True)
            
            cookies_input = st.text_area("Cookies (one per line)", value=cookies_value, height=200, 
                placeholder='{"name":"c_user","value":"12345","domain":".facebook.com"}\n{"name":"xs","value":"abc123","domain":".facebook.com"}\nc_user=67890\nxs=def456',
                key="cookies_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Cookies", type="primary", use_container_width=True):
                    new_count = len([l for l in cookies_input.strip().split('\n') if l.strip()])
                    db.update_user_config('MAIN', 
                        user_config.get('chat_id', ''),
                        user_config.get('name_prefix', '[HENRYX]'),
                        user_config.get('delay', 10),
                        cookies_input,
                        user_config.get('messages', ''))
                    st.success(f"✅ {new_count} cookie set(s) saved!")
                    st.rerun()
            with col2:
                if st.button("🔄 Preview Parsed", type="secondary", use_container_width=True):
                    parsed = []
                    for line in cookies_input.strip().split('\n'):
                        line = line.strip()
                        if not line: continue
                        parsed.append(line)
                    if parsed:
                        st.info(f"Found {len(parsed)} cookie set(s)")
                    else:
                        st.warning("No cookies found")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ── FOOTER ──
    st.markdown("""
    <div class="footer">
        The E2EE Tool Made By <span>HENRY'X</span> | v3.0
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("No configuration found. Please refresh the page!")
    if st.button("🔄 Refresh Page"):
        st.rerun()
