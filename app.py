import time
import threading
import os
import json
from flask import Flask, render_template_string, request, redirect, flash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import database as db

app = Flask(__name__)
app.secret_key = "henryx-2026"

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
    auto_state.logs.append(f"[{timestamp}] {msg}")
    if len(auto_state.logs) > 300:
        auto_state.logs = auto_state.logs[-200:]

def build_driver():
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
    return driver

def parse_cookies(cookies_text):
    if not cookies_text or not cookies_text.strip():
        return []
    all_cookies = []
    for line in cookies_text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            if line.startswith("{"):
                all_cookies.append(json.loads(line))
            elif line.startswith("["):
                items = json.loads(line)
                if isinstance(items, list):
                    all_cookies.extend(items)
            elif "=" in line:
                name, value = line.split("=", 1)
                all_cookies.append({"name": name.strip(), "value": value.strip(), "domain": ".facebook.com"})
        except:
            pass
    return all_cookies

def send_messages_loop(user_config):
    chat_id = user_config.get('chat_id', '')
    name_prefix = user_config.get('name_prefix', '[HENRYX]')
    delay = int(user_config.get('delay', 10))
    cookies_text = user_config.get('cookies', '')
    messages_text = user_config.get('messages', 'Hello')
    
    cookie_sets = parse_cookies(cookies_text)
    message_list = [m.strip() for m in messages_text.split('\n') if m.strip()]
    
    if not cookie_sets:
        cookie_sets = [None]
    if not message_list:
        message_list = ["Hello"]
    
    log_message(f'Target: {chat_id} | Cookies: {len(cookie_sets)} | Messages: {len(message_list)}')
    
    cycle = 0
    while not auto_state.stop_flag:
        driver = None
        try:
            log_message(f'Cycle {cycle+1}: Launching browser...')
            driver = build_driver()
            
            fb_url = f"https://www.facebook.com/messages/t/{chat_id}"
            driver.get(fb_url)
            time.sleep(10)
            
            # Apply cookies
            current_cookie = cookie_sets[cycle % len(cookie_sets)]
            if current_cookie:
                try:
                    if isinstance(current_cookie, dict):
                        driver.add_cookie(current_cookie)
                    elif isinstance(current_cookie, list):
                        for c in current_cookie:
                            try: driver.add_cookie(c)
                            except: pass
                    driver.get(fb_url)
                    time.sleep(8)
                except Exception as e:
                    log_message(f'Cookie error: {str(e)}')
            
            # Find input box
            msg_input = None
            selectors = [
                'div[contenteditable="true"][spellcheck="true"]',
                'div[role="textbox"]',
                'div[contenteditable="true"]',
                'textarea',
                'input[type="text"]'
            ]
            
            for sel in selectors:
                try:
                    els = driver.find_elements(By.CSS_SELECTOR, sel)
                    for el in els:
                        if el.is_displayed():
                            msg_input = el
                            break
                except:
                    pass
                if msg_input:
                    break
            
            if not msg_input:
                log_message('Message input not found - trying JS...')
                try:
                    el = driver.execute_script("""
                        const s = ['div[contenteditable="true"][spellcheck="true"]','div[role="textbox"]','div[contenteditable="true"]','textarea','input[type="text"]'];
                        for(let sel of s){ const e=document.querySelector(sel); if(e&&e.offsetParent!==null) return e; }
                        return null;
                    """)
                    if el:
                        msg_input = el
                except:
                    pass
            
            if not msg_input:
                log_message('Could not find message input - skipping cycle')
                cycle += 1
                if driver: driver.quit()
                time.sleep(delay)
                continue
            
            log_message('Message input found! Sending messages...')
            
            for i in range(len(message_list)):
                if auto_state.stop_flag:
                    break
                
                idx = (auto_state.message_rotation_index + i) % len(message_list)
                msg = message_list[idx]
                full = f"{name_prefix} {msg}" if name_prefix else msg
                
                try:
                    driver.execute_script("""
                        const el = arguments[0];
                        el.focus();
                        el.click();
                        if(el.tagName==='DIV'){ el.textContent=''; el.innerHTML=''; }
                        else { el.value=''; }
                    """, msg_input)
                    time.sleep(0.3)
                    
                    for ch in full:
                        if auto_state.stop_flag: break
                        driver.execute_script("""
                            const el=arguments[0]; const ch=arguments[1];
                            if(el.tagName==='DIV'){ el.textContent+=ch; }
                            else { el.value+=ch; }
                            el.dispatchEvent(new Event('input', {bubbles:true}));
                        """, msg_input, ch)
                        time.sleep(0.02)
                    
                    time.sleep(0.5)
                    
                    # Try send button
                    sent = False
                    try:
                        result = driver.execute_script("""
                            const btns = document.querySelectorAll('[aria-label*="Send" i]:not([aria-label*="like" i]), [data-testid="send-button"]');
                            for(let b of btns){
                                const el = b.closest('button') || b;
                                if(el.offsetParent!==null){ el.click(); return true; }
                            }
                            return false;
                        """)
                        if result:
                            sent = True
                    except:
                        pass
                    
                    if not sent:
                        # Enter key
                        try:
                            driver.execute_script("""
                                const el=arguments[0];
                                el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true}));
                                el.dispatchEvent(new KeyboardEvent('keyup',{key:'Enter',code:'Enter',keyCode:13,which:13,bubbles:true}));
                            """, msg_input)
                            sent = True
                        except:
                            pass
                    
                    auto_state.message_count += 1
                    log_message(f'Sent ({auto_state.message_count})')
                    
                    if auto_state.message_count % 30 == 0:
                        log_message('Cooling down 20s...')
                        time.sleep(20)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    log_message(f'Error sending msg: {str(e)}')
            
            auto_state.message_rotation_index += len(message_list)
            log_message(f'Cycle {cycle+1} complete. Waiting {delay}s...')
            
        except Exception as e:
            log_message(f'Cycle error: {str(e)}')
        finally:
            if driver:
                try: driver.quit()
                except: pass
        
        if auto_state.stop_flag:
            break
        cycle += 1
        time.sleep(delay)
    
    log_message('Automation stopped.')

def start_automation(user_config):
    if auto_state.running:
        return
    auto_state.running = True
    auto_state.stop_flag = False
    auto_state.message_count = 0
    auto_state.logs = []
    db.set_automation_running('MAIN', True)
    log_message('Starting automation...')
    thread = threading.Thread(target=send_messages_loop, args=(user_config,))
    thread.daemon = True
    thread.start()

def stop_automation():
    auto_state.running = False
    auto_state.stop_flag = True
    db.set_automation_running('MAIN', False)
    log_message('Stopping automation...')

# ── HTML ──
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>HENRY'X E2EE</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#0a0a12;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:20px}
        .container{max-width:800px;margin:0 auto}
        .header{text-align:center;padding:30px 0}
        .header h1{font-size:40px;background:linear-gradient(135deg,#ff1493,#8b00ff,#00d4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .header p{color:#888;font-size:13px;margin-top:5px}
        .card{background:#16162a;border:1px solid #2a2a4a;border-radius:14px;padding:25px;margin-bottom:20px}
        .card h2{font-size:18px;margin-bottom:15px;color:#fff}
        label{display:block;font-size:13px;color:#aaa;margin-bottom:4px;font-weight:600}
        input,textarea{width:100%;padding:12px;background:#0f0f1a;border:1px solid #2a2a4a;border-radius:8px;color:#fff;font-size:14px;margin-bottom:12px;outline:none}
        input:focus,textarea:focus{border-color:#8b00ff}
        textarea{font-family:monospace;font-size:13px;resize:vertical}
        .row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
        @media(max-width:600px){.row{grid-template-columns:1fr}}
        .btn{padding:12px 25px;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;transition:.3s;display:inline-block;margin:3px}
        .btn-primary{background:linear-gradient(135deg,#ff1493,#8b00ff);color:#fff}
        .btn-danger{background:linear-gradient(135deg,#ff3355,#cc0033);color:#fff}
        .btn-success{background:linear-gradient(135deg,#00cc66,#00994d);color:#fff}
        .btn-outline{background:transparent;border:1px solid #2a2a4a;color:#aaa}
        .btn:disabled{opacity:.4;cursor:not-allowed}
        .metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:15px}
        @media(max-width:600px){.metrics{grid-template-columns:1fr}}
        .metric{background:#0f0f1a;border:1px solid #2a2a4a;border-radius:10px;padding:15px;text-align:center}
        .metric .num{font-size:26px;font-weight:800;background:linear-gradient(135deg,#ff1493,#8b00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .metric .lbl{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-top:4px}
        .console{background:#050510;border:1px solid #2a2a4a;border-radius:10px;padding:15px;font-family:monospace;font-size:12px;line-height:1.8;max-height:350px;overflow-y:auto;margin-top:15px}
        .console .line{color:#888}
        .console .line::before{content:'> ';color:#8b00ff}
        .msg{display:none;padding:12px;border-radius:8px;margin-bottom:12px;font-weight:600}
        .msg.show{display:block}
        .msg.good{background:rgba(0,204,102,.15);border:1px solid #00cc66;color:#0c6}
        .msg.bad{background:rgba(255,51,85,.15);border:1px solid #ff3355;color:#f35}
        .footer{text-align:center;padding:30px;color:#555;font-size:13px}
        .footer span{background:linear-gradient(135deg,#ff1493,#8b00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>HENRY'X</h1>
        <p>OFFLINE E2EE AUTOMATION TOOL</p>
    </div>
    
    {% with m = get_flashed_messages(with_categories=true) %}
        {% if m %}
            {% for c, msg in m %}
                <div class="msg show {{ 'good' if c=='success' else 'bad' }}">{{ msg }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="card">
        <h2>⚙ Configuration</h2>
        <form method="POST" action="/save">
            <label>Chat / Conversation ID</label>
            <input type="text" name="chat_id" value="{{ c.chat_id }}" placeholder="Facebook Chat ID">
            
            <div class="row">
                <div>
                    <label>Name Prefix</label>
                    <input type="text" name="name_prefix" value="{{ c.name_prefix }}" placeholder="[HENRYX]">
                </div>
                <div>
                    <label>Delay (seconds)</label>
                    <input type="number" name="delay" value="{{ c.delay }}" min="1">
                </div>
            </div>
            
            <label>Messages (one per line)</label>
            <textarea name="messages" rows="5">{{ c.messages }}</textarea>
            
            <label>🍪 Cookies (one per line)</label>
            <textarea name="cookies" rows="5" placeholder='{"name":"c_user","value":"123","domain":".facebook.com"}
c_user=12345'>{{ c.cookies }}</textarea>
            
            <button type="submit" class="btn btn-success">💾 Save</button>
            <a href="/" class="btn btn-outline">🔄 Reload</a>
        </form>
    </div>
    
    <div class="card">
        <h2>▶ Automation</h2>
        <div class="metrics">
            <div class="metric"><div class="num">{{ count }}</div><div class="lbl">Messages Sent</div></div>
            <div class="metric"><div class="num" style="{% if running %}background:linear-gradient(135deg,#00ff88,#00cc66);-webkit-background-clip:text;-webkit-text-fill-color:transparent{% endif %}">{{ 'Running' if running else 'Stopped' }}</div><div class="lbl">Status</div></div>
            <div class="metric"><div class="num">{{ c.chat_id[:12]+'..' if c.chat_id else 'N/A' }}</div><div class="lbl">Chat ID</div></div>
        </div>
        
        <form method="POST" action="/start" style="display:inline">
            <button type="submit" class="btn btn-primary" {{ 'disabled' if running else '' }}>🚀 Start</button>
        </form>
        <form method="POST" action="/stop" style="display:inline">
            <button type="submit" class="btn btn-danger" {{ 'disabled' if not running else '' }}>⏹ Stop</button>
        </form>
        <a href="/" class="btn btn-outline">🔄 Refresh</a>
        
        <div class="console">
            {% if logs %}
                {% for log in logs[-40:] %}
                <div class="line">{{ log }}</div>
                {% endfor %}
            {% else %}
                <div class="line">Ready. Configure and start automation.</div>
            {% endif %}
        </div>
    </div>
    
    <div class="footer">The E2EE Tool Made By <span>HENRY'X</span></div>
</div>
<script>{% if running %}setTimeout(function(){location.reload()},3000){% endif %}</script>
</body>
</html>
"""

@app.route('/')
def index():
    config = db.get_user_config('MAIN')
    if not config:
        config = {'chat_id': '', 'name_prefix': '[HENRYX]', 'delay': 10, 'cookies': '', 'messages': 'Hello\nHi'}
    return render_template_string(HTML, c=config, running=auto_state.running, count=auto_state.message_count, logs=auto_state.logs)

@app.route('/save', methods=['POST'])
def save():
    db.update_user_config(
        'MAIN',
        request.form.get('chat_id', ''),
        request.form.get('name_prefix', '[HENRYX]'),
        int(request.form.get('delay', 10)),
        request.form.get('cookies', ''),
        request.form.get('messages', '')
    )
    flash('Configuration saved!', 'success')
    return redirect('/')

@app.route('/start', methods=['POST'])
def start():
    if auto_state.running:
        return redirect('/')
    config = db.get_user_config('MAIN')
    if not config or not config.get('chat_id') or config['chat_id'] in ['', 'Enter Your Chat Id']:
        flash('Set Chat ID first!', 'error')
        return redirect('/')
    start_automation(config)
    flash('Automation started!', 'success')
    return redirect('/')

@app.route('/stop', methods=['POST'])
def stop():
    stop_automation()
    flash('Automation stopped!', 'success')
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
