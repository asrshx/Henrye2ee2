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
from datetime import datetime
import queue
import sys

# ── PAGE CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="HENRY'X E2EE TOOL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CONSTANTS ──────────────────────────────────────────────────
WHATSAPP_NUMBER = "919919180262"
ADMIN_UID = "61564155712159"
APP_VERSION = "3.0.0"

# ── SESSION STATE (RAM Efficient) ─────────────────────────────
if 'automation_running' not in st.session_state:
    st.session_state.automation_running = False
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'auto_start_checked' not in st.session_state:
    st.session_state.auto_start_checked = False
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
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

# ── MODERN THEME CSS ──────────────────────────────────────────
MODERN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Rajdhani', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0d0b1a 100%);
        min-height: 100vh;
    }
    
    /* Animated Grid Background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: 
            linear-gradient(rgba(255,20,147,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,20,147,0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: 0;
    }
    
    /* Main Container - Glass Effect */
    .main .block-container {
        background: rgba(15, 10, 30, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 25px;
        border: 1px solid rgba(255,20,147,0.2);
        box-shadow: 0 8px 32px rgba(255,20,147,0.1);
        position: relative;
        z-index: 1;
    }
    
    /* HENRU'X Header */
    .henrux-header {
        text-align: center;
        padding: 20px;
        margin-bottom: 20px;
        position: relative;
    }
    
    .henrux-title {
        font-family: 'Orbitron', monospace;
        font-size: 3.5em;
        font-weight: 900;
        background: linear-gradient(90deg, #FF1493, #FF69B4, #FF1493);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite;
        text-shadow: none;
        letter-spacing: 4px;
    }
    
    @keyframes shimmer {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    
    .henrux-subtitle {
        font-family: 'Orbitron', monospace;
        color: rgba(255,255,255,0.5);
        font-size: 0.9em;
        letter-spacing: 8px;
        text-transform: uppercase;
        margin-top: -10px;
    }
    
    .henrux-version {
        color: rgba(255,20,147,0.4);
        font-size: 0.7em;
        font-family: 'Orbitron', monospace;
    }
    
    /* Profile Card - Modern */
    .profile-card-modern {
        background: linear-gradient(145deg, rgba(20,10,40,0.9), rgba(30,10,50,0.8));
        border-radius: 20px;
        border: 1px solid rgba(255,20,147,0.3);
        overflow: hidden;
        margin: 10px auto;
        max-width: 350px;
        box-shadow: 0 10px 40px rgba(255,20,147,0.15);
        transition: all 0.3s ease;
    }
    
    .profile-card-modern:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(255,20,147,0.25);
    }
    
    .profile-image-container {
        width: 100%;
        height: 200px;
        overflow: hidden;
        position: relative;
    }
    
    .profile-image-container::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 50px;
        background: linear-gradient(transparent, rgba(20,10,40,0.9));
    }
    
    .profile-image-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .profile-details-modern {
        padding: 20px;
        text-align: center;
    }
    
    .profile-name-modern {
        font-family: 'Orbitron', monospace;
        font-size: 1.8em;
        font-weight: 900;
        color: #FF1493;
        letter-spacing: 3px;
        margin: 0;
    }
    
    .profile-role-modern {
        font-family: 'Rajdhani', sans-serif;
        color: rgba(255,255,255,0.6);
        font-size: 0.85em;
        letter-spacing: 2px;
        margin: 5px 0;
    }
    
    .profile-status {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.7em;
        font-weight: 600;
        letter-spacing: 1px;
        margin-top: 8px;
    }
    
    .status-online {
        background: rgba(0,255,100,0.15);
        color: #00ff64;
        border: 1px solid rgba(0,255,100,0.3);
    }
    
    .status-offline {
        background: rgba(255,0,0,0.15);
        color: #ff4444;
        border: 1px solid rgba(255,0,0,0.3);
    }
    
    /* Buttons - Neon Style */
    .stButton>button {
        background: linear-gradient(90deg, #FF1493, #FF69B4) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 0.85em !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        letter-spacing: 2px !important;
        box-shadow: 0 4px 20px rgba(255,20,147,0.3) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(255,20,147,0.5) !important;
    }
    
    .stButton>button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }
    
    /* Input Fields - Cyber Style */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stNumberInput>div>div>input {
        background: rgba(10,5,20,0.8) !important;
        border: 1px solid rgba(255,20,147,0.3) !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1em !important;
        padding: 12px 15px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #FF1493 !important;
        box-shadow: 0 0 20px rgba(255,20,147,0.2) !important;
    }
    
    /* Labels */
    label {
        color: #FF69B4 !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
        letter-spacing: 1px !important;
    }
    
    /* Tabs - Modern */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(10,5,20,0.5);
        border-radius: 12px;
        padding: 5px;
        border: 1px solid rgba(255,20,147,0.2);
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255,255,255,0.5);
        border-radius: 8px;
        padding: 10px 20px;
        font-family: 'Orbitron', monospace;
        font-size: 0.75em;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #FF1493, #FF69B4) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255,20,147,0.3);
    }
    
    /* Metrics - Glowing */
    [data-testid="stMetricValue"] {
        color: #FF1493 !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 2.2em !important;
        font-weight: 900 !important;
        text-shadow: 0 0 20px rgba(255,20,147,0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.6) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.85em !important;
        letter-spacing: 1px !important;
    }
    
    /* Console - Hacker Style */
    .console-container {
        background: rgba(5,2,10,0.9);
        border: 1px solid rgba(255,20,147,0.2);
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .console-header {
        font-family: 'Orbitron', monospace;
        color: #FF1493;
        font-size: 0.8em;
        letter-spacing: 2px;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,20,147,0.2);
    }
    
    .console-line {
        font-family: 'Courier New', monospace;
        font-size: 0.8em;
        color: rgba(255,182,193,0.8);
        padding: 4px 8px;
        margin: 2px 0;
        border-left: 2px solid rgba(255,20,147,0.3);
        background: rgba(255,20,147,0.05);
        border-radius: 0 4px 4px 0;
    }
    
    .console-line.error {
        border-left-color: #ff4444;
        color: #ff6666;
    }
    
    .console-line.success {
        border-left-color: #00ff64;
        color: #66ff99;
    }
    
    /* Stats Cards */
    .stat-card {
        background: rgba(10,5,20,0.6);
        border: 1px solid rgba(255,20,147,0.15);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: rgba(255,20,147,0.4);
        box-shadow: 0 4px 20px rgba(255,20,147,0.1);
    }
    
    .stat-value {
        font-family: 'Orbitron', monospace;
        font-size: 2em;
        font-weight: 900;
        color: #FF1493;
    }
    
    .stat-label {
        color: rgba(255,255,255,0.5);
        font-size: 0.75em;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,20,147,0.3), transparent);
        margin: 20px 0;
    }
    
    /* Footer */
    .footer-modern {
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        border-top: 1px solid rgba(255,20,147,0.1);
        font-family: 'Orbitron', monospace;
        font-size: 0.7em;
        color: rgba(255,255,255,0.3);
        letter-spacing: 3px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: rgba(10,5,20,0.5); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #FF1493, #FF69B4); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #FF1493; }
    
    /* Success/Error Messages */
    .stAlert {
        background: rgba(10,5,20,0.8) !important;
        border: 1px solid rgba(255,20,147,0.3) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(10,5,20,0.5) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,20,147,0.2) !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 0.8em !important;
        color: #FF69B4 !important;
    }
</style>
"""

# ── HELPER FUNCTIONS ───────────────────────────────────────────
def log_message(msg, automation_state=None, level='info'):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    if automation_state:
        automation_state.logs.append(formatted_msg)
        if len(automation_state.logs) > 200:
            automation_state.logs = automation_state.logs[-150:]
    else:
        if 'logs' in st.session_state:
            st.session_state.logs.append(formatted_msg)
            if len(st.session_state.logs) > 200:
                st.session_state.logs = st.session_state.logs[-150:]
    
    # Queue for thread-safe logging
    try:
        st.session_state.log_queue.put_nowait({'msg': formatted_msg, 'level': level})
    except:
        pass

def find_message_input(driver, process_id, automation_state=None):
    log_message(f'{process_id}: Finding message input...', automation_state)
    time.sleep(8)

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    except Exception:
        pass

    try:
        page_title = driver.title
        page_url = driver.current_url
        log_message(f'{process_id}: Page: {page_title[:50]}', automation_state)
    except Exception as e:
        log_message(f'{process_id}: Page info error: {e}', automation_state)

    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[aria-label*="Message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        'div[data-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
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
                        try:
                            element.click()
                            time.sleep(0.3)
                        except:
                            pass

                        element_text = driver.execute_script("""
                            return arguments[0].placeholder || 
                                   arguments[0].getAttribute('aria-label') || 
                                   arguments[0].getAttribute('aria-placeholder') || '';
                        """, element).lower()

                        keywords = ['message', 'write', 'type', 'send', 'chat', 'msg', 'reply', 'text', 'aa']
                        if any(keyword in element_text for keyword in keywords):
                            return element
                        elif idx < 8:
                            return element
                except:
                    continue
        except:
            continue

    return None

def setup_browser(automation_state=None):
    log_message('Setting up Chrome browser...', automation_state)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--user-data-dir=/tmp/chrome-data')
    chrome_options.add_argument('--disable-dev-tools')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--mute-audio')
    chrome_options.add_argument('--safebrowsing-disable-auto-updates')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    # Chrome binary path
    chromium_paths = [
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome',
        '/usr/bin/chrome',
        '/snap/bin/chromium'
    ]

    for chromium_path in chromium_paths:
        if Path(chromium_path).exists():
            chrome_options.binary_location = chromium_path
            log_message(f'Found Chromium at: {chromium_path}', automation_state)
            break
    else:
        log_message('Chromium not found at standard paths!', automation_state)
        try:
            result = subprocess.run(['which', 'chromium', 'chromium-browser', 'chrome', 'google-chrome'], 
                                   capture_output=True, text=True)
            log_message(f'Available: {result.stdout}', automation_state)
        except:
            pass

    # ChromeDriver path
    chromedriver_paths = [
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver',
        '/snap/bin/chromedriver'
    ]

    driver_path = None
    for driver_candidate in chromedriver_paths:
        if Path(driver_candidate).exists():
            driver_path = driver_candidate
            log_message(f'Found ChromeDriver at: {driver_path}', automation_state)
            break

    try:
        from selenium.webdriver.chrome.service import Service
        
        if driver_path:
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        driver.set_window_size(1920, 1080)
        log_message('Chrome browser setup completed!', automation_state)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state)
        raise error

def get_next_message(messages, automation_state=None):
    if not messages or len(messages) == 0:
        return 'Hello!'

    if automation_state:
        message = messages[automation_state.message_rotation_index % len(messages)]
        automation_state.message_rotation_index += 1
    else:
        message = messages[0]

    return message

def send_messages(config, automation_state, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state)
        automation_state.start_time = time.time()
        
        driver = setup_browser(automation_state)

        log_message(f'{process_id}: Navigating to Facebook...', automation_state)
        driver.get('https://www.facebook.com/')
        time.sleep(8)

        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state)
            cookie_array = config['cookies'].split(';')
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

        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state)
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state)
            driver.get('https://www.facebook.com/messages')

        time.sleep(15)

        message_input = find_message_input(driver, process_id, automation_state)

        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state, 'error')
            automation_state.running = False
            db.set_automation_running(process_id, False)
            return 0

        delay = int(config['delay'])
        messages_sent = 0
        messages_list = [msg.strip() for msg in config['messages'].split('\n') if msg.strip()]

        if not messages_list:
            messages_list = ['Hello!']

        while automation_state.running:
            try:
                base_message = get_next_message(messages_list, automation_state)

                if config['name_prefix']:
                    message_to_send = f"{config['name_prefix']} {base_message}"
                else:
                    message_to_send = base_message

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
                    log_message(f'{process_id}: Sent: "{message_to_send[:25]}..."', automation_state, 'success')
                else:
                    log_message(f'{process_id}: Sent: "{message_to_send[:25]}..."', automation_state, 'success')

                messages_sent += 1
                automation_state.message_count = messages_sent
                automation_state.consecutive_errors = 0

                time.sleep(delay)

            except Exception as e:
                automation_state.consecutive_errors += 1
                automation_state.error_count += 1
                log_message(f'{process_id}: Error: {str(e)[:60]}', automation_state, 'error')
                
                if automation_state.consecutive_errors >= 5:
                    log_message(f'{process_id}: Too many errors, restarting browser...', automation_state, 'error')
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                    driver = setup_browser(automation_state)
                    driver.get(f'https://www.facebook.com/messages/t/{config["chat_id"]}')
                    time.sleep(15)
                    message_input = find_message_input(driver, process_id, automation_state)
                    automation_state.consecutive_errors = 0
                
                time.sleep(5)

        log_message(f'{process_id}: Stopped. Total: {messages_sent}', automation_state, 'success')
        return messages_sent

    except Exception as e:
        log_message(f'{process_id}: Fatal: {str(e)}', automation_state, 'error')
        automation_state.running = False
        db.set_automation_running(process_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state)
            except:
                pass

def send_admin_notification(user_config, process_id, automation_state=None):
    driver = None
    try:
        log_message(f"ADMIN: Preparing notification...", automation_state)
        driver = setup_browser(automation_state)

        driver.get('https://www.facebook.com/')
        time.sleep(8)

        if user_config['cookies'] and user_config['cookies'].strip():
            cookie_array = user_config['cookies'].split(';')
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

        log_message(f"ADMIN: Opening admin profile...", automation_state)
        driver.get(f'https://www.facebook.com/{ADMIN_UID}')
        time.sleep(8)

        message_button_selectors = [
            'div[aria-label*="Message" i]',
            'a[aria-label*="Message" i]',
            '[data-testid*="message"]'
        ]

        for selector in message_button_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for elem in elements:
                        text = elem.text.lower() if elem.text else ""
                        aria_label = elem.get_attribute('aria-label') or ""
                        if 'message' in text or 'message' in aria_label.lower():
                            driver.execute_script("arguments[0].click();", elem)
                            time.sleep(8)
                            break
                    break
            except:
                continue

        message_input = find_message_input(driver, 'ADMIN', automation_state)

        if message_input:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notification_msg = f"⚡ HENRY'X Automation Started at {current_time}"

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
            """, message_input, notification_msg)

            time.sleep(1)

            send_result = driver.execute_script("""
                const sendButtons = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                for (let btn of sendButtons) {
                    if (btn.offsetParent !== null) {
                        btn.click();
                        return 'button_clicked';
                    }
                }
                return 'button_not_found';
            """)

            if send_result == 'button_not_found':
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

            time.sleep(2)
            log_message(f"ADMIN: Notification sent", automation_state, 'success')
        else:
            log_message(f"ADMIN: Message input not found", automation_state, 'error')

    except Exception as e:
        log_message(f"ADMIN: Error: {str(e)}", automation_state, 'error')
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def run_automation_with_notification(user_config, automation_state, process_id='AUTO-1'):
    send_admin_notification(user_config, process_id, automation_state)
    send_messages(user_config, automation_state, process_id)

def start_automation(user_config):
    automation_state = st.session_state.automation_state

    if automation_state.running:
        return

    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    automation_state.start_time = time.time()
    automation_state.error_count = 0
    automation_state.consecutive_errors = 0

    db.set_automation_running('MAIN', True)

    thread = threading.Thread(target=run_automation_with_notification, args=(user_config, automation_state))
    thread.daemon = True
    thread.start()

def stop_automation():
    st.session_state.automation_state.running = False
    db.set_automation_running('MAIN', False)

def format_uptime(seconds):
    if seconds is None:
        return "00:00:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# ── APPLY CSS ──────────────────────────────────────────────────
st.markdown(MODERN_CSS, unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="henrux-header">
    <div class="henrux-title">HENRY'X</div>
    <div class="henrux-subtitle">E2EE Automation System</div>
    <div class="henrux-version">v{APP_VERSION}</div>
</div>
""", unsafe_allow_html=True)

# ── PROFILE CARD ──────────────────────────────────────────────
st.markdown("""
<div class="profile-card-modern">
    <div class="profile-image-container">
        <img src="https://i.imgur.com/mp3KrYJ.jpeg">
    </div>
    <div class="profile-details-modern">
        <div class="profile-name-modern">HENRU'X</div>
        <div class="profile-role-modern">E2EE Automation Tool</div>
        <div class="profile-status status-online">● SYSTEM ACTIVE</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MAIN CONTENT ──────────────────────────────────────────────
user_config = db.get_user_config('MAIN')

if user_config:
    tab1, tab2, tab3 = st.tabs(["⚙️ CONFIG", "🚀 AUTOMATION", "📊 STATS"])

    with tab1:
        st.markdown("### Configuration Panel")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chat_id = st.text_input("Chat ID", value=user_config['chat_id'], placeholder="Enter Facebook Chat ID...")
            name_prefix = st.text_input("Name Prefix", value=user_config['name_prefix'], placeholder="[HENRU'X]")
            delay = st.number_input("Delay (seconds)", min_value=1, max_value=3600, value=user_config['delay'])
        
        with col2:
            cookies = st.text_area("Cookies (optional)", placeholder="Paste Facebook cookies...", height=100)
            messages = st.text_area("Messages (one per line)", value=user_config['messages'], height=150)

        if st.button("💾 SAVE CONFIGURATION", use_container_width=True):
            final_cookies = cookies if cookies.strip() else user_config['cookies']
            db.update_user_config('MAIN', chat_id, name_prefix, delay, final_cookies, messages)
            st.success("✅ Configuration saved successfully!")
            st.rerun()

    with tab2:
        st.markdown("### Automation Control Center")
        
        # Status Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Messages Sent", st.session_state.automation_state.message_count)
        
        with col2:
            status = "🟢 RUNNING" if st.session_state.automation_state.running else "🔴 STOPPED"
            st.metric("Status", status)
        
        with col3:
            uptime = 0
            if st.session_state.automation_state.start_time and st.session_state.automation_state.running:
                uptime = time.time() - st.session_state.automation_state.start_time
            st.metric("Uptime", format_uptime(uptime))
        
        with col4:
            st.metric("Errors", st.session_state.automation_state.error_count)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 START AUTOMATION", 
                        disabled=st.session_state.automation_state.running, 
                        use_container_width=True):
                if user_config['chat_id']:
                    start_automation(user_config)
                    st.success("✅ Automation started!")
                    st.rerun()
                else:
                    st.error("❌ Please set Chat ID in Configuration first!")
        
        with col2:
            if st.button("⏹️ STOP AUTOMATION", 
                        disabled=not st.session_state.automation_state.running, 
                        use_container_width=True):
                stop_automation()
                st.warning("⏹️ Automation stopped!")
                st.rerun()
        
        # Live Console
        if st.session_state.automation_state.logs:
            st.markdown("### Live Console")
            
            console_html = '<div class="console-container"><div class="console-header">⟐ CONSOLE OUTPUT</div>'
            for log in st.session_state.automation_state.logs[-40:]:
                css_class = "console-line"
                if "error" in log.lower() or "fail" in log.lower():
                    css_class += " error"
                elif "sent" in log.lower() or "success" in log.lower():
                    css_class += " success"
                console_html += f'<div class="{css_class}">{log}</div>'
            console_html += '</div>'
            
            st.markdown(console_html, unsafe_allow_html=True)
            
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()

    with tab3:
        st.markdown("### System Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">""" + str(st.session_state.automation_state.message_count) + """</div>
                <div class="stat-label">Total Messages</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">""" + str(st.session_state.automation_state.error_count) + """</div>
                <div class="stat-label">Total Errors</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stat-card">
                <div class="stat-value">""" + format_uptime(uptime) + """</div>
                <div class="stat-label">Session Uptime</div>
            </div>
            """, unsafe_allow_html=True)
            
            status_text = "Active" if st.session_state.automation_state.running else "Inactive"
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{status_text}</div>
                <div class="stat-label">System Status</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Logs", use_container_width=True):
                st.session_state.automation_state.logs = []
                st.session_state.logs = []
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset Counter", use_container_width=True):
                st.session_state.automation_state.message_count = 0
                st.session_state.automation_state.error_count = 0
                st.rerun()
        
        with col3:
            if st.button("📋 Copy Logs", use_container_width=True):
                log_text = "\n".join(st.session_state.automation_state.logs[-50:])
                st.code(log_text, language="bash")
else:
    st.warning("⚠️ No configuration found. Please refresh the page!")

# ── FOOTER ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer-modern">
    HENRY'X E2EE SYSTEM v{APP_VERSION} | MADE WITH ⚡ | 24/7 AUTOMATION
</div>
""", unsafe_allow_html=True)
