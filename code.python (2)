import time
import threading
import uuid
import hashlib
import os
import subprocess
import json
import urllib.parse
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests
import base64

app = Flask(__name__)
app.secret_key = "henryx-secure-key-2026"

WHATSAPP_NUMBER = "919919180262"
ADMIN_UID = "100001493272464"

class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0
        self.stop_flag = False

auto_state = AutomationState()

def log_message(msg):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    auto_state.logs.append(formatted_msg)
    if len(auto_state.logs) > 500:
        auto_state.logs = auto_state.logs[-300:]

def build_driver(cookie_string=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    if cookie_string and cookie_string.strip():
        try:
            cookies_list = json.loads(cookie_string)
            if isinstance(cookies_list, list):
                for c in cookies_list:
                    try:
                        driver.add_cookie(c)
                    except:
                        pass
        except:
            pass
    
    return driver

def parse_cookies_multi(cookies_text):
    if not cookies_text or not cookies_text.strip():
        return []
    all_cookies = []
    lines = cookies_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("{"):
            try:
                cookie_obj = json.loads(line)
                all_cookies.append(cookie_obj)
                continue
            except:
                pass
        if line.startswith("["):
            try:
                cookie_list = json.loads(line)
                if isinstance(cookie_list, list):
                    all_cookies.extend(cookie_list)
                continue
            except:
                pass
        parts = line.split("\t")
        if len(parts) >= 7:
            cookie = {
                "domain": parts[0], "flag": parts[1], "path": parts[2],
                "secure": parts[3].lower() == "true", "expiry": parts[4],
                "name": parts[5], "value": parts[6]
            }
            all_cookies.append(cookie)
        elif "=" in line:
            name, value = line.split("=", 1)
            all_cookies.append({"name": name.strip(), "value": value.strip(), "domain": ".facebook.com"})
    return all_cookies

def find_message_input(driver, process_id):
    log_message(f'{process_id}: Finding message input...')
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
                    log_message(f'{process_id}: Found input via: {selector}')
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
            log_message(f'{process_id}: Found input via JS')
            return driver.execute_script("return arguments[0];", result)
        log_message(f'{process_id}: No message input found')
        return None
    except Exception as e:
        log_message(f'{process_id}: Error: {str(e)}')
        return None

def type_message(driver, element, message):
    try:
        driver.execute_script("""
            const el = arguments[0];
            el.focus();
            el.click();
            if (el.tagName === 'DIV') { el.textContent = ''; el.innerHTML = ''; }
            else { el.value = ''; }
        """, element)
        time.sleep(0.5)
        for char in message:
            if auto_state.stop_flag:
                return False
            driver.execute_script("""
                const el = arguments[0];
                const char = arguments[1];
                el.focus();
                if (el.tagName === 'DIV') { el.textContent += char; }
                else { el.value += char; }
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, element, char)
            time.sleep(0.03)
        return True
    except:
        return False

def send_message(driver, element):
    try:
        result = driver.execute_script("""
            const sendBtns = document.querySelectorAll(
                '[aria-label*="Send" i]:not([aria-label*="like" i]), ' +
                '[data-testid="send-button"], button[aria-label="Send"]'
            );
            for (let btn of sendBtns) {
                const clickable = btn.closest('button') || btn;
                if (clickable.offsetParent !== null) { clickable.click(); return 'clicked'; }
            }
            return 'not_found';
        """)
        if result == 'not_found':
            driver.execute_script("""
                const el = arguments[0];
                el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                el.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
            """, element)
            return 'enter'
        return 'button'
    except:
        return 'error'

def send_messages(user_config, process_id='AUTO-1'):
    chat_id = user_config.get('chat_id', '')
    name_prefix = user_config.get('name_prefix', '[HENRYX]')
    delay = user_config.get('delay', 10)
    cookies_text = user_config.get('cookies', '')
    messages_text = user_config.get('messages', 'Hello')
    
    cookie_sets = parse_cookies_multi(cookies_text)
    message_list = [m.strip() for m in messages_text.split('\n') if m.strip()]
    
    log_message(f'{process_id}: Started for chat {chat_id}')
    log_message(f'{process_id}: {len(cookie_sets)} cookie sets, {len(message_list)} messages')
    
    if not cookie_sets:
        cookie_sets = [None]
    
    cookie_index = 0
    while not auto_state.stop_flag:
        driver = None
        try:
            log_message(f'{process_id}: Launching browser (cookie set {cookie_index % len(cookie_sets) + 1})...')
            driver = build_driver()
            fb_url = f"https://www.facebook.com/messages/t/{chat_id}"
            driver.get(fb_url)
            log_message(f'{process_id}: Navigated to chat')
            time.sleep(8)
            
            if cookie_sets[cookie_index % len(cookie_sets)]:
                c = cookie_sets[cookie_index % len(cookie_sets)]
                if isinstance(c, list):
                    for cc in c:
                        try: driver.add_cookie(cc)
                        except: pass
                elif isinstance(c, dict):
                    try: driver.add_cookie(c)
                    except: pass
                driver.get(fb_url)
                time.sleep(8)
            
            msg_input = find_message_input(driver, process_id)
            if not msg_input:
                log_message(f'{process_id}: Input not found, skipping cycle')
                cookie_index += 1
                if driver: driver.quit()
                time.sleep(delay)
                continue
            
            for msg_idx in range(len(message_list)):
                if auto_state.stop_flag: break
                actual_idx = (auto_state.message_rotation_index + msg_idx) % len(message_list)
                message = message_list[actual_idx]
                full_msg = f"{name_prefix} {message}" if name_prefix else message
                log_message(f'{process_id}: Sending msg {actual_idx+1}/{len(message_list)}')
                if type_message(driver, msg_input, full_msg):
                    time.sleep(1)
                    result = send_message(driver, msg_input)
                    auto_state.message_count += 1
                    log_message(f'{process_id}: Sent! ({auto_state.message_count} total)')
                    if auto_state.message_count % 50 == 0:
                        log_message('Cool-down 30s...')
                        time.sleep(30)
                    time.sleep(2)
            
            auto_state.message_rotation_index += len(message_list)
            log_message(f'{process_id}: Cycle done. Wait {delay}s...')
        except Exception as e:
            log_message(f'{process_id}: Error: {str(e)}')
        finally:
            if driver:
                try: driver.quit()
                except: pass
        if auto_state.stop_flag: break
        cookie_index += 1
        time.sleep(delay)
    log_message(f'{process_id}: Stopped')

def run_automation_with_notification(user_config, process_id='AUTO-1'):
    log_message("ADMIN: Sending notification...")
    try:
        driver = build_driver()
        driver.get(f"https://web.whatsapp.com/send?phone={WHATSAPP_NUMBER}")
        log_message("ADMIN: Opening WhatsApp...")
        time.sleep(15)
        msg_input = find_message_input(driver, "ADMIN")
        if msg_input:
            msg = f"HENRYX E2EE Started\nChat: {user_config.get('chat_id','')}\nTime: {time.strftime('%H:%M:%S')}"
            driver.execute_script("arguments[0].textContent = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));", msg_input, msg)
            time.sleep(1)
            driver.execute_script("""
                const btns = document.querySelectorAll('[aria-label*=\"Send\" i]');
                for(let b of btns){ if(b.offsetParent!==null){ b.click(); break; } }
            """)
        driver.quit()
        log_message("ADMIN: Notification sent")
    except Exception as e:
        log_message(f"ADMIN: Error: {str(e)}")

def start_automation(user_config):
    if auto_state.running: return
    auto_state.running = True
    auto_state.stop_flag = False
    auto_state.message_count = 0
    db.set_automation_running('MAIN', True)
    thread = threading.Thread(target=run_automation_with_notification, args=(user_config,))
    thread.daemon = True
    thread.start()

def stop_automation():
    auto_state.running = False
    auto_state.stop_flag = True
    db.set_automation_running('MAIN', False)

# ── HTML PAGE ──
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>HENRY'X - E2EE Tool</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #0a0a12; 
            color: #e0e0e0; 
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; padding: 30px 0; }
        .header h1 { 
            font-size: 42px; 
            background: linear-gradient(135deg, #ff1493, #8b00ff, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p { color: #888; font-size: 14px; margin-top: 5px; }
        
        .card { 
            background: #16162a; 
            border: 1px solid #2a2a4a; 
            border-radius: 14px; 
            padding: 25px; 
            margin-bottom: 20px;
        }
        .card h2 { font-size: 18px; margin-bottom: 18px; color: #fff; }
        
        label { display: block; font-size: 13px; color: #aaa; margin-bottom: 5px; font-weight: 600; }
        input, textarea, select {
            width: 100%;
            padding: 12px 14px;
            background: #0f0f1a;
            border: 1px solid #2a2a4a;
            border-radius: 10px;
            color: #fff;
            font-size: 14px;
            margin-bottom: 15px;
            outline: none;
        }
        input:focus, textarea:focus { border-color: #8b00ff; }
        textarea { font-family: 'Courier New', monospace; font-size: 13px; resize: vertical; }
        
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        @media(max-width:600px) { .row { grid-template-columns: 1fr; } }
        
        .btn {
            padding: 14px 30px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-block;
            margin: 5px;
        }
        .btn-primary { background: linear-gradient(135deg, #ff1493, #8b00ff); color: #fff; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(139,0,255,0.3); }
        .btn-danger { background: linear-gradient(135deg, #ff3355, #cc0033); color: #fff; }
        .btn-success { background: linear-gradient(135deg, #00cc66, #00994d); color: #fff; }
        .btn-outline { background: transparent; border: 1px solid #2a2a4a; color: #aaa; }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none !important; }
        
        .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
        @media(max-width:600px) { .metrics { grid-template-columns: 1fr; } }
        .metric {
            background: #0f0f1a;
            border: 1px solid #2a2a4a;
            border-radius: 10px;
            padding: 18px;
            text-align: center;
        }
        .metric .num { font-size: 28px; font-weight: 800; background: linear-gradient(135deg, #ff1493, #8b00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .metric .lbl { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }
        
        .console {
            background: #050510;
            border: 1px solid #2a2a4a;
            border-radius: 10px;
            padding: 18px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.8;
            max-height: 350px;
            overflow-y: auto;
            margin-top: 15px;
        }
        .console .line { color: #888; }
        .console .line::before { content: '> '; color: #8b00ff; }
        
        .flash { 
            padding: 12px 18px; 
            border-radius: 10px; 
            margin-bottom: 15px; 
            font-weight: 600;
            display: none;
        }
        .flash.success { display: block; background: rgba(0,204,102,0.15); border: 1px solid #00cc66; color: #00cc66; }
        .flash.error { display: block; background: rgba(255,51,85,0.15); border: 1px solid #ff3355; color: #ff3355; }
        
        .footer { text-align: center; padding: 30px; color: #555; font-size: 13px; }
        .footer span { background: linear-gradient(135deg, #ff1493, #8b00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>HENRY'X</h1>
        <p>OFFLINE E2EE AUTOMATION TOOL</p>
    </div>
    
    {% with msgs = get_flashed_messages(with_categories=true) %}
        {% if msgs %}
            {% for cat, msg in msgs %}
                <div class="flash {{ cat }}">{{ msg }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <!-- CONFIG CARD -->
    <div class="card">
        <h2>⚙ Configuration</h2>
        <form method="POST" action="/save">
            <label>Chat / Conversation ID</label>
            <input type="text" name="chat_id" value="{{ config.chat_id }}" placeholder="Facebook Chat ID">
            
            <div class="row">
                <div>
                    <label>Name Prefix</label>
                    <input type="text" name="name_prefix" value="{{ config.name_prefix }}" placeholder="[HENRYX]">
                </div>
                <div>
                    <label>Delay (seconds)</label>
                    <input type="number" name="delay" value="{{ config.delay }}" min="1">
                </div>
            </div>
            
            <label>Messages (one per line)</label>
            <textarea name="messages" rows="6">{{ config.messages }}</textarea>
            
            <label>🍪 Cookies (one per line - JSON / name=value / Netscape)</label>
            <textarea name="cookies" rows="6" placeholder='{"name":"c_user","value":"123","domain":".facebook.com"}
{"name":"xs","value":"abc","domain":".facebook.com"}
c_user=12345'>{{ config.cookies }}</textarea>
            
            <button type="submit" class="btn btn-success">💾 Save Configuration</button>
            <a href="/" class="btn btn-outline">🔄 Reload</a>
        </form>
    </div>
    
    <!-- AUTOMATION CARD -->
    <div class="card">
        <h2>▶ Automation Control</h2>
        <div class="metrics">
            <div class="metric">
                <div class="num">{{ msg_count }}</div>
                <div class="lbl">Messages Sent</div>
            </div>
            <div class="metric">
                <div class="num" style="{% if is_running %}background:linear-gradient(135deg,#00ff88,#00cc66);-webkit-background-clip:text;-webkit-text-fill-color:transparent{% endif %}">{{ 'Running' if is_running else 'Stopped' }}</div>
                <div class="lbl">Status</div>
            </div>
            <div class="metric">
                <div class="num">{{ config.chat_id[:12] + '...' if config.chat_id else 'N/A' }}</div>
                <div class="lbl">Target Chat</div>
            </div>
        </div>
        
        <form method="POST" action="/start" style="display:inline">
            <button type="submit" class="btn btn-primary" {% if is_running %}disabled{% endif %}>🚀 Start Automation</button>
        </form>
        <form method="POST" action="/stop" style="display:inline">
            <button type="submit" class="btn btn-danger" {% if not is_running %}disabled{% endif %}>⏹ Stop Automation</button>
        </form>
        <a href="/" class="btn btn-outline">🔄 Refresh</a>
        
        {% if logs %}
        <div class="console">
            {% for log in logs[-40:] %}
            <div class="line">{{ log }}</div>
            {% endfor %}
        </div>
        {% else %}
        <div class="console">
            <div class="line">Waiting for actions...</div>
        </div>
        {% endif %}
    </div>
    
    <div class="footer">
        The E2EE Tool Made By <span>HENRY'X</span> | v3.0
    </div>
</div>
<script>
    // Auto-refresh every 3 seconds agar automation chal raha hai
    {% if is_running %}
    setTimeout(function(){
        window.location.reload();
    }, 3000);
    {% endif %}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    config = db.get_user_config('MAIN')
    if not config:
        config = {'chat_id': '', 'name_prefix': '[HENRYX]', 'delay': 10, 'cookies': '', 'messages': 'Hello\nHi'}
    return render_template_string(HTML, config=config, is_running=auto_state.running, msg_count=auto_state.message_count, logs=auto_state.logs[-40:])

@app.route('/save', methods=['POST'])
def save():
    chat_id = request.form.get('chat_id', '')
    name_prefix = request.form.get('name_prefix', '[HENRYX]')
    delay = int(request.form.get('delay', 10))
    cookies = request.form.get('cookies', '')
    messages = request.form.get('messages', '')
    
    db.update_user_config('MAIN', chat_id, name_prefix, delay, cookies, messages)
    
    # Flash message through cookie/session
    from flask import flash
    flash('Configuration saved successfully!', 'success')
    return redirect('/')

@app.route('/start', methods=['POST'])
def start():
    if auto_state.running:
        return redirect('/')
    
    config = db.get_user_config('MAIN')
    if not config or not config.get('chat_id') or config.get('chat_id') in ['', 'Enter Your Chat Id']:
        from flask import flash
        flash('Error: Chat ID is not set!', 'error')
        return redirect('/')
    
    start_automation(config)
    from flask import flash
    flash('Automation started!', 'success')
    return redirect('/')

@app.route('/stop', methods=['POST'])
def stop():
    stop_automation()
    from flask import flash
    flash('Automation stopped!', 'success')
    return redirect('/')

# ── MAIN ──
if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║        HENRY'X - E2EE TOOL v3.0     ║
    ║     Offline Automation System        ║
    ╚══════════════════════════════════════╝
    """)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
