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
app.secret_key = "henryx-final"

class AutoState:
    def __init__(self):
        self.running = False
        self.msg_count = 0
        self.logs = []
        self.rot_idx = 0
        self.stop = False

state = AutoState()

def log(m):
    state.logs.append(f"[{time.strftime('%H:%M:%S')}] {m}")
    if len(state.logs) > 300:
        state.logs = state.logs[-200:]

def build_driver():
    o = Options()
    for arg in ["--headless","--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
                "--window-size=1920,1080","--disable-blink-features=AutomationControlled"]:
        o.add_argument(arg)
    o.add_experimental_option("excludeSwitches",["enable-automation"])
    return webdriver.Chrome(options=o)

def parse_cookies(text):
    if not text or not text.strip(): return []
    out = []
    for line in text.strip().split("\n"):
        line=line.strip()
        if not line or line.startswith("#"): continue
        try:
            if line.startswith("{"):
                d=json.loads(line)
                if isinstance(d,dict): out.append(d)
            elif line.startswith("["):
                for x in json.loads(line):
                    if isinstance(x,dict): out.append(x)
            elif "=" in line:
                n,v=line.split("=",1)
                out.append({"name":n.strip(),"value":v.strip(),"domain":".facebook.com","path":"/"})
        except: pass
    return out

def automation_loop(config):
    cid=config.get('chat_id','')
    pf=config.get('name_prefix','[HENRYX]')
    delay=int(config.get('delay',10))
    cookie_text=config.get('cookies','')
    msg_text=config.get('messages','Hello')
    
    cookies=parse_cookies(cookie_text)
    msgs=[m.strip() for m in msg_text.split('\n') if m.strip()]
    if not msgs: msgs=["Hello"]
    
    log(f"Target: {cid} | Cookies: {len(cookies)} | Messages: {len(msgs)}")
    
    cycle=0
    while not state.stop:
        driver=None
        try:
            log(f"Cycle {cycle+1}: Starting...")
            driver=build_driver()
            
            # 👉 PEHLE FACEBOOK LOAD KARO (cookie set karne se pehle domain chahiye)
            driver.get("https://facebook.com")
            time.sleep(5)
            
            # 👉 AB COOKIES SET KARO
            if cookies:
                c=cookies[cycle%len(cookies)]
                try:
                    driver.add_cookie(c)
                    log(f"Cookie: {c.get('name','?')}={c.get('value','?')[:15]}...")
                except Exception as e:
                    log(f"Cookie error: {str(e)[:40]}")
            else:
                log("No cookies - proceeding without login")
            
            # 👉 AB CHAT PAR JAO
            driver.get(f"https://www.facebook.com/messages/t/{cid}")
            time.sleep(10)
            
            # 👉 INPUT DHUNDHO
            inp=None
            for sel in ['div[contenteditable="true"][spellcheck="true"]','div[role="textbox"]',
                        'div[contenteditable="true"]','textarea','input[type="text"]']:
                try:
                    for el in driver.find_elements(By.CSS_SELECTOR,sel):
                        if el.is_displayed(): inp=el; break
                except: pass
                if inp: break
            
            if not inp:
                try:
                    inp=driver.execute_script("""
                        for(let s of ['div[contenteditable="true"][spellcheck="true"]','div[role="textbox"]',
                            'div[contenteditable="true"]','textarea','input[type="text"]']){
                            let e=document.querySelector(s);
                            if(e&&e.offsetParent!==null) return e;
                        } return null;
                    """)
                except: pass
            
            if not inp:
                log("Input not found - login failed or invalid cookies")
                driver.save_screenshot(f"/tmp/debug_{cycle}.png")
                cycle+=1
                time.sleep(delay)
                continue
            
            log("Input found! Sending messages...")
            
            for i in range(len(msgs)):
                if state.stop: break
                idx=(state.rot_idx+i)%len(msgs)
                full=f"{pf} {msgs[idx]}" if pf else msgs[idx]
                
                try:
                    driver.execute_script("""
                        const el=arguments[0]; el.focus(); el.click();
                        if(el.tagName==='DIV'){el.textContent='';el.innerHTML='';}
                        else{el.value='';}
                    """,inp)
                    time.sleep(0.3)
                    
                    for ch in full:
                        if state.stop: break
                        driver.execute_script("""
                            const el=arguments[0],ch=arguments[1];
                            if(el.tagName==='DIV')el.textContent+=ch; else el.value+=ch;
                            el.dispatchEvent(new Event('input',{bubbles:true}));
                        """,inp,ch)
                        time.sleep(0.02)
                    
                    time.sleep(0.5)
                    sent=False
                    try:
                        r=driver.execute_script("""
                            for(let b of document.querySelectorAll('[aria-label*=\"Send\" i],[data-testid=\"send-button\"]')){
                                let e=b.closest('button')||b;
                                if(e.offsetParent!==null){e.click();return true;}
                            } return false;
                        """)
                        if r: sent=True
                    except: pass
                    
                    if not sent:
                        driver.execute_script("""
                            const el=arguments[0];
                            el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',keyCode:13,bubbles:true}));
                            el.dispatchEvent(new KeyboardEvent('keyup',{key:'Enter',keyCode:13,bubbles:true}));
                        """,inp)
                    
                    state.msg_count+=1
                    log(f"Sent ({state.msg_count})")
                    
                    if state.msg_count%30==0:
                        log("Cooldown 20s..."); time.sleep(20)
                    time.sleep(2)
                except Exception as e:
                    log(f"Send error: {str(e)[:40]}")
            
            state.rot_idx+=len(msgs)
            log(f"Cycle {cycle+1} done. Wait {delay}s...")
        except Exception as e:
            log(f"Error: {str(e)[:50]}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
        if state.stop: break
        cycle+=1
        time.sleep(delay)
    
    log("Stopped.")

def start():
    if state.running: return
    state.running=True; state.stop=False; state.msg_count=0; state.logs=[]
    log("Starting...")
    c=db.get_user_config('MAIN')
    threading.Thread(target=automation_loop,args=(c,),daemon=True).start()

def stop():
    state.running=False; state.stop=True
    log("Stopping...")

PAGE="""
<!DOCTYPE html>
<html>
<head><title>HENRY'X</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a12;color:#e0e0e0;font-family:Segoe UI,sans-serif;padding:20px}
.c{max-width:750px;margin:0 auto}
.h{text-align:center;padding:25px 0}
.h h1{font-size:38px;background:linear-gradient(135deg,#ff1493,#8b00ff,#00d4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.h p{color:#888;font-size:13px}
.card{background:#16162a;border:1px solid #2a2a4a;border-radius:12px;padding:22px;margin-bottom:18px}
.card h2{font-size:17px;margin-bottom:14px;color:#fff}
label{display:block;font-size:12px;color:#aaa;margin-bottom:3px;font-weight:600}
input,textarea{width:100%;padding:11px 13px;background:#0f0f1a;border:1px solid #2a2a4a;border-radius:8px;color:#fff;font-size:14px;margin-bottom:10px;outline:none}
input:focus,textarea:focus{border-color:#8b00ff}
textarea{font-family:monospace;font-size:12px;resize:vertical}
.r{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:600px){.r{grid-template-columns:1fr}}
.btn{padding:11px 22px;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;margin:3px;display:inline-block;transition:.2s}
.btn-p{background:linear-gradient(135deg,#ff1493,#8b00ff);color:#fff}
.btn-d{background:linear-gradient(135deg,#ff3355,#cc0033);color:#fff}
.btn-g{background:linear-gradient(135deg,#00cc66,#00994d);color:#fff}
.btn-o{background:transparent;border:1px solid #2a2a4a;color:#aaa}
.btn:disabled{opacity:.4;cursor:default}
.m{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px}
@media(max-width:600px){.m{grid-template-columns:1fr}}
.mb{background:#0f0f1a;border:1px solid #2a2a4a;border-radius:8px;padding:14px;text-align:center}
.mb .n{font-size:24px;font-weight:800;background:linear-gradient(135deg,#ff1493,#8b00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.mb .l{font-size:10px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-top:3px}
.console{background:#050510;border:1px solid #2a2a4a;border-radius:8px;padding:14px;font-family:monospace;font-size:12px;line-height:1.7;max-height:320px;overflow-y:auto;margin-top:12px}
.console .ln{color:#888}
.console .ln::before{content:'> ';color:#8b00ff}
.flash{display:none;padding:10px 14px;border-radius:8px;margin-bottom:10px;font-weight:600}
.flash.show{display:block}
.flash.ok{background:rgba(0,204,102,.12);border:1px solid #0c6;color:#0c6}
.flash.bad{background:rgba(255,51,85,.12);border:1px solid #f35;color:#f35}
.f{text-align:center;padding:25px;color:#555;font-size:12px}
.f span{background:linear-gradient(135deg,#ff1493,#8b00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
</style></head>
<body>
<div class=c>
<div class=h><h1>HENRY'X</h1><p>OFFLINE E2EE AUTOMATION TOOL</p></div>
{% with m=get_flashed_messages(with_categories=true) %}{% if m %}{% for c,msg in m %}<div class="flash show {{'ok' if c=='success' else 'bad'}}">{{msg}}</div>{% endfor %}{% endif %}{% endwith %}

<div class=card>
<h2>⚙ Configuration</h2>
<form method=POST action=/save>
<label>Chat ID</label>
<input name=chat_id value="{{c.chat_id}}" placeholder="Facebook Chat ID">
<div class=r>
<div><label>Name Prefix</label><input name=name_prefix value="{{c.name_prefix}}" placeholder="[HENRYX]"></div>
<div><label>Delay (sec)</label><input type=number name=delay value="{{c.delay}}" min=1></div>
</div>
<label>Messages (one per line)</label><textarea name=messages rows=5>{{c.messages}}</textarea>
<label>🍪 Cookies (one per line)</label><textarea name=cookies rows=5 placeholder='{"name":"c_user","value":"123","domain":".facebook.com"}'></textarea>
<button type=submit class="btn btn-g">💾 Save</button>
<a href=/ class="btn btn-o">🔄 Reload</a>
</form></div>

<div class=card>
<h2>▶ Automation</h2>
<div class=m>
<div class=mb><div class=n>{{count}}</div><div class=l>Sent</div></div>
<div class=mb><div class=n style="{%if running%}background:linear-gradient(135deg,#00ff88,#00cc66);-webkit-background-clip:text;-webkit-text-fill-color:transparent{%endif%}">{{'Running'if running else'Stopped'}}</div><div class=l>Status</div></div>
<div class=mb><div class=n>{{c.chat_id[:12]+'..'if c.chat_id else'---'}}</div><div class=l>Chat ID</div></div>
</div>

<form method=POST action=/start style=display:inline><button class="btn btn-p" {{'disabled'if running else''}}>🚀 Start</button></form>
<form method=POST action=/stop style=display:inline><button class="btn btn-d" {{'disabled'if not running else''}}>⏹ Stop</button></form>
<a href=/ class="btn btn-o">🔄 Refresh</a>

<div class=console>
{%if logs%}{%for l in logs[-40:]%}<div class=ln>{{l}}</div>{%endfor%}
{%else%}<div class=ln>Ready.</div>{%endif%}
</div></div>

<div class=f>Made By <span>HENRY'X</span></div></div>
<script>{%if running%}setTimeout(function(){location.reload()},3000){%endif%}</script>
</body></html>
"""

@app.route('/')
def idx():
    c=db.get_user_config('MAIN')
    if not c: c={'chat_id':'','name_prefix':'[HENRYX]','delay':10,'cookies':'','messages':'Hello\nHi'}
    return render_template_string(PAGE,c=c,running=state.running,count=state.msg_count,logs=state.logs)

@app.route('/save',methods=['POST'])
def save():
    db.update_user_config('MAIN',request.form.get('chat_id',''),request.form.get('name_prefix','[HENRYX]'),
                          int(request.form.get('delay',10)),request.form.get('cookies',''),request.form.get('messages',''))
    flash('Saved!','success'); return redirect('/')

@app.route('/start',methods=['POST'])
def st():
    if state.running: return redirect('/')
    c=db.get_user_config('MAIN')
    if not c or not c.get('chat_id') or c['chat_id'] in ['','Enter Your Chat Id']:
        flash('Set Chat ID first!','error'); return redirect('/')
    start(); flash('Started!','success'); return redirect('/')

@app.route('/stop',methods=['POST'])
def sp():
    stop(); flash('Stopped!','success'); return redirect('/')

if __name__=='__main__':
    port=int(os.environ.get("PORT",8080))
    app.run(host='0.0.0.0',port=port,debug=False,threaded=True)
