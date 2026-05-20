# app.py - HENRY'X - Complete Redesign
# Author: Rebuilt for HENRY'X
# No Streamlit - Pure Flask + Modern UI

import time
import threading
import uuid
import hashlib
import os
import subprocess
import json
import urllib.parse
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import database as db
import requests
import base64

app = Flask(__name__)
app.secret_key = "henryx-secure-key-2026"

# ── CONFIG ──
WHATSAPP_NUMBER = "919919180262"
ADMIN_UID = "100001493272464"

# ── Automation State ──
class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0
        self.stop_flag = False

auto_state = AutomationState()

# ── LOG HELPER ──
def log_message(msg):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    auto_state.logs.append(formatted_msg)
    if len(auto_state.logs) > 500:
        auto_state.logs = auto_state.logs[-300:]

# ── CHROME DRIVER BUILDER ──
def build_driver(cookie_string=None, proxy=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """
    })

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

# ── COOKIE PARSER (Multi-Cookie Support - One Per Line) ──
def parse_cookies_multi(cookies_text):
    """
    Supports multiple cookies, one per line.
    Each line can be:
    - JSON object string
    - "name=value" format
    - Raw Netscape cookie format
    Returns list of cookie dicts
    """
    if not cookies_text or not cookies_text.strip():
        return []

    all_cookies = []
    lines = cookies_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Try JSON format
        if line.startswith("{"):
            try:
                cookie_obj = json.loads(line)
                all_cookies.append(cookie_obj)
                continue
            except:
                pass

        # Try JSON array format
        if line.startswith("["):
            try:
                cookie_list = json.loads(line)
                if isinstance(cookie_list, list):
                    all_cookies.extend(cookie_list)
                continue
            except:
                pass

        # Try Netscape / "name=value" format
        parts = line.split("\t")
        if len(parts) >= 7:
            # Netscape cookie format
            cookie = {
                "domain": parts[0],
                "flag": parts[1],
                "path": parts[2],
                "secure": parts[3].lower() == "true",
                "expiry": parts[4],
                "name": parts[5],
                "value": parts[6]
            }
            all_cookies.append(cookie)
        elif "=" in line:
            # Simple name=value
            name, value = line.split("=", 1)
            all_cookies.append({"name": name.strip(), "value": value.strip(), "domain": ".facebook.com"})

    return all_cookies

# ── FIND MESSAGE INPUT ──
def find_message_input(driver, process_id):
    log_message(f'{process_id}: Finding message input...')
    time.sleep(10)

    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Try multiple selector strategies
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

        # JavaScript fallback
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
            // Last resort: find any visible input
            const all = document.querySelectorAll('input, textarea, div[contenteditable]');
            for (let el of all) {
                if (el.offsetParent !== null) return el;
            }
            return null;
        """)

        if result:
            log_message(f'{process_id}: Found input via JS fallback')
            return driver.execute_script("return arguments[0];", result)

        log_message(f'{process_id}: No message input found')
        return None

    except Exception as e:
        log_message(f'{process_id}: Error finding input: {str(e)}')
        return None

# ── TYPE MESSAGE ──
def type_message(driver, element, message):
    try:
        driver.execute_script("""
            const el = arguments[0];
            el.focus();
            el.click();
            if (el.tagName === 'DIV') {
                el.textContent = '';
                el.innerHTML = '';
            } else {
                el.value = '';
            }
        """, element)

        time.sleep(0.5)

        # Type character by character for realism
        for char in message:
            if auto_state.stop_flag:
                return False
            driver.execute_script("""
                const el = arguments[0];
                const char = arguments[1];
                el.focus();
                if (el.tagName === 'DIV') {
                    el.textContent += char;
                } else {
                    el.value += char;
                }
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            """, element, char)
            time.sleep(0.05)

        return True
    except Exception as e:
        log_message(f"Error typing message: {str(e)}")
        return False

# ── SEND MESSAGE ──
def send_message(driver, element):
    try:
        # Try clicking send button first
        result = driver.execute_script("""
            const sendBtns = document.querySelectorAll(
                '[aria-label*="Send" i]:not([aria-label*="like" i]), ' +
                '[data-testid="send-button"], ' +
                'button[aria-label="Send"], ' +
                'svg[aria-label="Send"]'
            );
            for (let btn of sendBtns) {
                const clickable = btn.closest('button') || btn;
                if (clickable.offsetParent !== null) {
                    clickable.click();
                    return 'clicked';
                }
            }
            return 'not_found';
        """)

        if result == 'not_found':
            # Press Enter instead
            driver.execute_script("""
                const el = arguments[0];
                el.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                }));
                el.dispatchEvent(new KeyboardEvent('keyup', {
                    key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                }));
            """, element)
            return 'enter_key'
        return 'button_clicked'
    except Exception as e:
        log_message(f"Error sending: {str(e)}")
        return 'error'

# ── SEND MESSAGES (MAIN LOOP) ──
def send_messages(user_config, process_id='AUTO-1'):
    chat_id = user_config.get('chat_id', '')
    name_prefix = user_config.get('name_prefix', '[HENRYX]')
    delay = user_config.get('delay', 10)
    cookies_text = user_config.get('cookies', '')
    messages_text = user_config.get('messages', 'Hello')

    cookie_sets = parse_cookies_multi(cookies_text)
    message_list = [m.strip() for m in messages_text.split('\n') if m.strip()]

    log_message(f'{process_id}: Starting message loop for chat {chat_id}')
    log_message(f'{process_id}: Loaded {len(cookie_sets)} cookie set(s)')
    log_message(f'{process_id}: Loaded {len(message_list)} message(s)')

    if not cookie_sets:
        cookie_sets = [None]  # No cookies mode

    cookie_index = 0

    while not auto_state.stop_flag:
        current_cookies = cookie_sets[cookie_index % len(cookie_sets)]

        driver = None
        try:
            log_message(f'{process_id}: Launching browser (cookie set {cookie_index % len(cookie_sets) + 1}/{len(cookie_sets)})...')

            if current_cookies and isinstance(current_cookies, dict) and 'name' in current_cookies:
                cookie_json = json.dumps([current_cookies])
            elif current_cookies and isinstance(current_cookies, list):
                cookie_json = json.dumps(current_cookies)
            else:
                cookie_json = None

            driver = build_driver(cookie_json)

            # Open Messenger
            fb_url = f"https://www.facebook.com/messages/t/{chat_id}"
            driver.get(fb_url)
            log_message(f'{process_id}: Navigated to chat')
            time.sleep(5)

            # In case of cookie set, reload after cookies are added
            if current_cookies:
                if isinstance(current_cookies, list):
                    for c in current_cookies:
                        try:
                            driver.add_cookie(c)
                        except:
                            pass
                elif isinstance(current_cookies, dict):
                    try:
                        driver.add_cookie(current_cookies)
                    except:
                        pass
                driver.get(fb_url)
                time.sleep(5)

            # Find message input
            msg_input = find_message_input(driver, process_id)
            if not msg_input:
                log_message(f'{process_id}: Could not find input, skipping this cycle')
                cookie_index += 1
                if driver:
                    driver.quit()
                time.sleep(delay)
                continue

            # Send messages in rotation
            for msg_idx in range(len(message_list)):
                if auto_state.stop_flag:
                    break

                msg_idx_actual = (auto_state.message_rotation_index + msg_idx) % len(message_list)
                message = message_list[msg_idx_actual]
                full_message = f"{name_prefix} {message}" if name_prefix else message

                log_message(f'{process_id}: Sending message {msg_idx_actual + 1}/{len(message_list)}')

                if type_message(driver, msg_input, full_message):
                    time.sleep(1)
                    result = send_message(driver, msg_input)
                    auto_state.message_count += 1
                    log_message(f'{process_id}: Sent! Method: {result} (Total: {auto_state.message_count})')

                    # Check if we got temp blocked
                    if auto_state.message_count % 50 == 0:
                        log_message(f'{process_id}: Reached {auto_state.message_count} messages - cooling down 30s')
                        time.sleep(30)

                    time.sleep(2)

            auto_state.message_rotation_index += len(message_list)
            log_message(f'{process_id}: Cycle complete. Waiting {delay}s before next...')

        except Exception as e:
            log_message(f'{process_id}: Error: {str(e)}')
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        if auto_state.stop_flag:
            break

        cookie_index += 1
        time.sleep(delay)

    log_message(f'{process_id}: Automation stopped')

# ── SEND ADMIN NOTIFICATION ──
def send_admin_notification(user_config, process_id='AUTO-1'):
    log_message(f"ADMIN-NOTIFY: Sending admin notification...")

    chat_id = user_config.get('chat_id', '')
    notification_msg = f"🤖 HENRY'X E2EE Tool Started\n━━━━━━━━━━━━━━━\nTarget Chat: {chat_id}\nProcess ID: {process_id}\nTime: {time.strftime('%H:%M:%S')}\nStatus: Automation Activated ✅"

    driver = None
    try:
        driver = build_driver()

        # Open WhatsApp Web
        driver.get(f"https://web.whatsapp.com/send?phone={WHATSAPP_NUMBER}")
        log_message(f"ADMIN-NOTIFY: Opening WhatsApp...")
        time.sleep(15)

        # Find message input
        msg_input = find_message_input(driver, "ADMIN-NOTIFY")
        if msg_input:
            log_message(f"ADMIN-NOTIFY: Found message input, typing...")
            time.sleep(2)

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
            """, msg_input, notification_msg)
            time.sleep(1)

            send_result = driver.execute_script("""
                const sendButtons = document.querySelectorAll(
                    '[aria-label*="Send" i]:not([aria-label*="like" i]), ' +
                    '[data-testid="send-button"]'
                );
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
                    element.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                    }));
                    element.dispatchEvent(new KeyboardEvent('keyup', {
                        key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                    }));
                """, msg_input)
                log_message(f"ADMIN-NOTIFY: Sent via Enter key")
            else:
                log_message(f"ADMIN-NOTIFY: Send button clicked")

            time.sleep(2)
        else:
            log_message(f"ADMIN-NOTIFY: Failed to find message input")

    except Exception as e:
        log_message(f"ADMIN-NOTIFY: Error: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f"ADMIN-NOTIFY: Browser closed")
            except:
                pass

def run_automation_with_notification(user_config, process_id='AUTO-1'):
    send_admin_notification(user_config, process_id)
    send_messages(user_config, process_id)

# ── FLASK ROUTES ──

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HENRY'X - E2EE Automation Tool</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a2e;
            --bg-card-hover: #22223a;
            --border-color: #2a2a4a;
            --text-primary: #e8e8f0;
            --text-secondary: #8888aa;
            --text-muted: #555577;
            --accent-1: #ff1493;
            --accent-2: #8b00ff;
            --accent-3: #00d4ff;
            --success: #00ff88;
            --warning: #ffaa00;
            --danger: #ff3355;
            --gradient-main: linear-gradient(135deg, #ff1493, #8b00ff, #00d4ff);
            --gradient-glow: linear-gradient(135deg, rgba(255,20,147,0.3), rgba(139,0,255,0.3), rgba(0,212,255,0.3));
            --shadow-glow: 0 0 40px rgba(139,0,255,0.15);
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated Background */
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(ellipse at 20% 50%, rgba(255,20,147,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(139,0,255,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 80%, rgba(0,212,255,0.06) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        .container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 1;
        }

        /* HEADER */
        .header {
            text-align: center;
            padding: 40px 20px 30px;
            position: relative;
        }

        .header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 2px;
            background: var(--gradient-main);
            border-radius: 2px;
        }

        .logo-img {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid transparent;
            background: var(--gradient-main);
            padding: 3px;
            margin-bottom: 15px;
            box-shadow: var(--shadow-glow);
        }

        .logo-text {
            font-size: 48px;
            font-weight: 900;
            background: var(--gradient-main);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-bottom: 8px;
            text-shadow: none;
        }

        .logo-text .x-mark {
            -webkit-text-fill-color: initial;
            color: var(--accent-1);
        }

        .subtitle {
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 400;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .subtitle span {
            color: var(--accent-1);
        }

        /* TABS */
        .tabs {
            display: flex;
            gap: 4px;
            background: var(--bg-secondary);
            border-radius: 14px;
            padding: 5px;
            margin: 25px 0 30px;
            border: 1px solid var(--border-color);
        }

        .tab-btn {
            flex: 1;
            padding: 14px 24px;
            border: none;
            background: transparent;
            color: var(--text-muted);
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
        }

        .tab-btn.active {
            background: var(--gradient-main);
            color: white;
            box-shadow: 0 4px 20px rgba(139,0,255,0.3);
        }

        .tab-btn:hover:not(.active) {
            color: var(--text-primary);
            background: var(--bg-card);
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* CARDS */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: rgba(139,0,255,0.3);
            box-shadow: 0 0 30px rgba(139,0,255,0.08);
        }

        .card-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card-title .icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: var(--gradient-main);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }

        /* FORM */
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .form-group.full { grid-column: 1 / -1; }

        label {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            letter-spacing: 0.5px;
        }

        input, textarea, select {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 16px;
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            transition: all 0.3s ease;
            outline: none;
            width: 100%;
        }

        input:focus, textarea:focus, select:focus {
            border-color: var(--accent-2);
            box-shadow: 0 0 20px rgba(139,0,255,0.15);
        }

        textarea {
            resize: vertical;
            min-height: 100px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            line-height: 1.6;
        }

        select {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%238888aa' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10l-5 5z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 14px center;
        }

        /* BUTTONS */
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 12px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            letter-spacing: 0.5px;
        }

        .btn-primary {
            background: var(--gradient-main);
            color: white;
            box-shadow: 0 4px 25px rgba(139,0,255,0.25);
        }

        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 40px rgba(139,0,255,0.35);
        }

        .btn-danger {
            background: linear-gradient(135deg, var(--danger), #ff0044);
            color: white;
            box-shadow: 0 4px 25px rgba(255,51,85,0.25);
        }

        .btn-danger:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 40px rgba(255,51,85,0.35);
        }

        .btn-outline {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
        }

        .btn-outline:hover {
            border-color: var(--accent-2);
            color: var(--text-primary);
        }

        .btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none !important;
        }

        .btn-group {
            display: flex;
            gap: 12px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        /* METRICS */
        .metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }

        .metric {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }

        .metric-value {
            font-size: 32px;
            font-weight: 800;
            background: var(--gradient-main);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .metric-label {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .metric.status-running .metric-value {
            background: linear-gradient(135deg, var(--success), #00cc66);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .metric.status-stopped .metric-value {
            background: linear-gradient(135deg, var(--text-muted), #444466);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* CONSOLE */
        .console {
            background: #050510;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            line-height: 1.8;
            max-height: 400px;
            overflow-y: auto;
            margin-top: 15px;
            position: relative;
        }

        .console::before {
            content: 'CONSOLE OUTPUT';
            position: sticky;
            top: 0;
            display: block;
            font-family: 'Inter', sans-serif;
            font-size: 10px;
            font-weight: 600;
            color: var(--text-muted);
            letter-spacing: 2px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-color);
            background: #050510;
        }

        .console-line {
            color: var(--text-secondary);
            word-break: break-all;
        }

        .console-line::before {
            content: '>';
            color: var(--accent-2);
            margin-right: 8px;
        }

        .console-line.info { color: var(--accent-3); }
        .console-line.success { color: var(--success); }
        .console-line.warning { color: var(--warning); }
        .console-line.error { color: var(--danger); }

        .console::-webkit-scrollbar {
            width: 6px;
        }

        .console::-webkit-scrollbar-track {
            background: transparent;
        }

        .console::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 3px;
        }

        /* TOGGLE SWITCH */
        .toggle-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .toggle {
            position: relative;
            width: 48px;
            height: 26px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 13px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .toggle.active {
            background: var(--gradient-main);
            border-color: var(--accent-2);
        }

        .toggle::after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            transition: all 0.3s ease;
        }

        .toggle.active::after {
            left: 24px;
        }

        .toggle-label {
            font-size: 13px;
            color: var(--text-secondary);
        }

        /* FOOTER */
        .footer {
            text-align: center;
            padding: 30px 20px;
            margin-top: 40px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 13px;
        }

        .footer span {
            background: var(--gradient-main);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }

        /* RESPONSIVE */
        @media (max-width: 768px) {
            .form-grid { grid-template-columns: 1fr; }
            .metrics { grid-template-columns: 1fr; }
            .logo-text { font-size: 32px; }
            .tabs { flex-direction: column; }
        }

        @media (max-width: 480px) {
            .container { padding: 10px; }
            .card { padding: 20px; }
        }

        /* ANIMATIONS */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .pulse {
            animation: pulse 2s ease-in-out infinite;
        }

        /* COOKIE BADGE */
        .cookie-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(139,0,255,0.15);
            color: var(--accent-2);
            border: 1px solid rgba(139,0,255,0.3);
        }

        .cookie-badge.success {
            background: rgba(0,255,136,0.1);
            color: var(--success);
            border-color: rgba(0,255,136,0.3);
        }

        /* NOTIFICATION TOAST */
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            border-radius: 12px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            z-index: 1000;
            transform: translateX(120%);
            transition: transform 0.4s ease;
            max-width: 400px;
        }

        .toast.show { transform: translateX(0); }
        .toast.success { border-color: var(--success); }
        .toast.error { border-color: var(--danger); }
        .toast .toast-title { font-weight: 700; font-size: 14px; margin-bottom: 4px; }
        .toast .toast-msg { font-size: 13px; color: var(--text-secondary); }
    </style>
</head>
<body>

<div class="container">
    <!-- HEADER -->
    <header class="header">
        <img src="https://i.imgur.com/mp3KrYJ.jpeg" alt="HENRYX" class="logo-img" onerror="this.style.display='none'">
        <h1 class="logo-text">HENRY<span class="x-mark">'X</span></h1>
        <p class="subtitle">Offline <span>E2EE</span> Automation Tool</p>
    </header>

    <!-- TABS -->
    <div class="tabs">
        <button class="tab-btn active" data-tab="config">⚙ Configuration</button>
        <button class="tab-btn" data-tab="automation">▶ Automation</button>
        <button class="tab-btn" data-tab="cookies">🍪 Multi-Cookies</button>
        <button class="tab-btn" data-tab="about">ℹ About</button>
    </div>

    <!-- TAB: CONFIGURATION -->
    <div class="tab-content active" id="tab-config">
        <div class="card">
            <div class="card-title">
                <span class="icon">⚙</span>
                Tool Configuration
            </div>
            <div class="form-grid">
                <div class="form-group full">
                    <label>Chat / Conversation ID</label>
                    <input type="text" id="chat_id" value="{{ config.chat_id }}" placeholder="Enter Facebook Chat ID...">
                </div>
                <div class="form-group">
                    <label>Name Prefix</label>
                    <input type="text" id="name_prefix" value="{{ config.name_prefix }}" placeholder="[HENRYX]">
                </div>
                <div class="form-group">
                    <label>Delay Between Cycles (seconds)</label>
                    <input type="number" id="delay" value="{{ config.delay }}" min="1" step="1">
                </div>
                <div class="form-group full">
                    <label>Messages (one per line)</label>
                    <textarea id="messages" rows="8" placeholder="Type your messages here...&#10;One per line">{{ config.messages }}</textarea>
                </div>
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" onclick="saveConfig()">💾 Save Configuration</button>
                <button class="btn btn-outline" onclick="loadConfig()">🔄 Reload</button>
            </div>
        </div>
    </div>

    <!-- TAB: AUTOMATION -->
    <div class="tab-content" id="tab-automation">
        <div class="card">
            <div class="card-title">
                <span class="icon">▶</span>
                Automation Control Panel
            </div>

            <div class="metrics">
                <div class="metric">
                    <div class="metric-value" id="msgCount">0</div>
                    <div class="metric-label">Messages Sent</div>
                </div>
                <div class="metric" id="statusMetric">
                    <div class="metric-value" id="statusVal">Stopped</div>
                    <div class="metric-label">Status</div>
                </div>
                <div class="metric">
                    <div class="metric-value" id="chatIdDisplay">{{ config.chat_id[:15] + '...' if config.chat_id else 'N/A' }}</div>
                    <div class="metric-label">Target Chat ID</div>
                </div>
            </div>

            <div class="btn-group">
                <button class="btn btn-primary" id="startBtn" onclick="startAuto()">🚀 Start Automation</button>
                <button class="btn btn-danger" id="stopBtn" onclick="stopAuto()" disabled>⏹ Stop Automation</button>
                <button class="btn btn-outline" onclick="refreshStatus()">🔄 Refresh</button>
            </div>

            <div class="console" id="console">
                <div class="console-line info">[{{ time }}] HENRY'X E2EE Tool initialized</div>
                <div class="console-line info">[{{ time }}] Waiting for user action...</div>
            </div>
        </div>
    </div>

    <!-- TAB: MULTI-COOKIES -->
    <div class="tab-content" id="tab-cookies">
        <div class="card">
            <div class="card-title">
                <span class="icon">🍪</span>
                Multi-Cookie Manager
            </div>
            <p style="color: var(--text-secondary); font-size: 14px; margin-bottom: 15px;">
                Paste one cookie per line. Supports JSON format, Netscape format, or simple <code>name=value</code>.
                Each line = separate cookie set. The tool will rotate through all sets automatically.
            </p>
            <div class="form-group">
                <label>Cookies (one cookie per line)</label>
                <textarea id="cookies" rows="12" placeholder='{"name":"c_user","value":"12345","domain":".facebook.com"}
{"name":"xs","value":"abcd","domain":".facebook.com"}
c_user=67890
xs=efgh' style="font-size: 12px;">{{ config.cookies }}</textarea>
            </div>
            <div style="margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="cookie-badge" id="cookieCount">0 cookie sets loaded</span>
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" onclick="saveCookies()">💾 Save Cookies</button>
                <button class="btn btn-outline" onclick="parseCookiePreview()">🔍 Preview Parsed</button>
            </div>
            <div id="cookiePreview" style="margin-top: 15px; display: none;">
                <div class="card" style="padding: 15px;">
                    <div style="font-size: 13px; color: var(--text-secondary); white-space: pre-wrap; font-family: 'JetBrains Mono', monospace;"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB: ABOUT -->
    <div class="tab-content" id="tab-about">
        <div class="card">
            <div class="card-title">
                <span class="icon">ℹ</span>
                About HENRY'X E2EE Tool
            </div>
            <div style="color: var(--text-secondary); font-size: 14px; line-height: 1.8;">
                <p><strong style="color: var(--text-primary);">Version:</strong> 3.0</p>
                <p><strong style="color: var(--text-primary);">Type:</strong> Offline E2EE Automation Tool</p>
                <p><strong style="color: var(--text-primary);">Engine:</strong> Selenium WebDriver + Chromium</p>
                <p><strong style="color: var(--text-primary);">Features:</strong></p>
                <ul style="padding-left: 20px; margin: 8px 0;">
                    <li>Multi-Cookie support (one per line, auto-rotate)</li>
                    <li>Message rotation system</li>
                    <li>Admin notification via WhatsApp</li>
                    <li>Cookie rotation across sessions</li>
                    <li>Real-time console output</li>
                    <li>Anti-detection measures</li>
                </ul>
                <p style="margin-top: 15px;">
                    Made with <span style="color: var(--accent-1);">❤</span> by
                    <strong style="background: var(--gradient-main); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">HENRY'X</strong>
                </p>
            </div>
        </div>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        The E2EE Tool Made By <span>HENRY'X</span> | v3.0
    </div>
</div>

<!-- TOAST -->
<div class="toast" id="toast">
    <div class="toast-title" id="toastTitle">Success</div>
    <div class="toast-msg" id="toastMsg">Configuration saved!</div>
</div>

<script>
    const API_BASE = '';

    // ── TABS ──
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            document.getElementById('tab-' + this.dataset.tab).classList.add('active');
        });
    });

    // ── TOAST ──
    function showToast(title, msg, type = 'success') {
        const toast = document.getElementById('toast');
        document.getElementById('toastTitle').textContent = title;
        document.getElementById('toastMsg').textContent = msg;
        toast.className = 'toast ' + type;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3500);
    }

    // ── SAVE CONFIG ──
    async function saveConfig() {
        const data = {
            chat_id: document.getElementById('chat_id').value,
            name_prefix: document.getElementById('name_prefix').value,
            delay: parseInt(document.getElementById('delay').value) || 10,
            messages: document.getElementById('messages').value
        };

        try {
            const res = await fetch('/api/save-config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            if (result.success) {
                showToast('Saved', 'Configuration saved successfully!', 'success');
            } else {
                showToast('Error', result.error || 'Failed to save', 'error');
            }
        } catch(e) {
            showToast('Error', 'Connection error', 'error');
        }
    }

    async function loadConfig() {
        try {
            const res = await fetch('/api/get-config');
            const data = await res.json();
            if (data.success) {
                document.getElementById('chat_id').value = data.config.chat_id;
                document.getElementById('name_prefix').value = data.config.name_prefix;
                document.getElementById('delay').value = data.config.delay;
                document.getElementById('messages').value = data.config.messages;
                document.getElementById('cookies').value = data.config.cookies;
                showToast('Loaded', 'Configuration reloaded', 'success');
            }
        } catch(e) {
            showToast('Error', 'Failed to load config', 'error');
        }
    }

    // ── COOKIES ──
    async function saveCookies() {
        const cookies = document.getElementById('cookies').value;
        try {
            const res = await fetch('/api/save-cookies', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cookies: cookies})
            });
            const result = await res.json();
            if (result.success) {
                document.getElementById('cookieCount').textContent = result.count + ' cookie sets parsed';
                showToast('Saved', result.count + ' cookie set(s) saved!', 'success');
            }
        } catch(e) {
            showToast('Error', 'Failed to save cookies', 'error');
        }
    }

    async function parseCookiePreview() {
        const cookies = document.getElementById('cookies').value;
        try {
            const res = await fetch('/api/parse-cookies', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({cookies: cookies})
            });
            const result = await res.json();
            const preview = document.getElementById('cookiePreview');
            preview.style.display = 'block';
            const content = preview.querySelector('.card div');
            if (result.success) {
                content.innerHTML = '<strong style="color: var(--success);">Parsed ' + result.count + ' cookie set(s):</strong>\\n\\n' +
                    result.sets.map((s, i) =>
                        'Set #' + (i+1) + ': ' + (typeof s === 'string' ? s : JSON.stringify(s, null, 2))
                    ).join('\\n\\n---\\n\\n');
            } else {
                content.innerHTML = '<span style="color: var(--danger);">Failed to parse: ' + (result.error || 'unknown error') + '</span>';
            }
        } catch(e) {
            showToast('Error', 'Parse error', 'error');
        }
    }

    // ── AUTOMATION ──
    async function startAuto() {
        try {
            const res = await fetch('/api/start', {method: 'POST'});
            const result = await res.json();
            if (result.success) {
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                updateStatus('Running');
                showToast('Started', 'Automation has been started!', 'success');
                startPolling();
            } else {
                showToast('Error', result.error || 'Failed to start', 'error');
            }
        } catch(e) {
            showToast('Error', 'Connection error', 'error');
        }
    }

    async function stopAuto() {
        try {
            const res = await fetch('/api/stop', {method: 'POST'});
            const result = await res.json();
            if (result.success) {
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                updateStatus('Stopped');
                showToast('Stopped', 'Automation has been stopped', 'warning');
            }
        } catch(e) {
            showToast('Error', 'Connection error', 'error');
        }
    }

    async function refreshStatus() {
        try {
            const res = await fetch('/api/status');
            const result = await res.json();
            if (result.success) {
                document.getElementById('msgCount').textContent = result.message_count;
                document.getElementById('chatIdDisplay').textContent =
                    (result.chat_id || 'N/A').substring(0, 15) + '...';
                if (result.running) {
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    updateStatus('Running');
                } else {
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    updateStatus('Stopped');
                }
                updateConsole(result.logs);
            }
        } catch(e) {
            console.error(e);
        }
    }

    function updateStatus(status) {
        const el = document.getElementById('statusVal');
        el.textContent = status;
        const metric = document.getElementById('statusMetric');
        metric.className = 'metric status-' + (status === 'Running' ? 'running' : 'stopped');
    }

    function updateConsole(logs) {
        const console = document.getElementById('console');
        if (!logs || logs.length === 0) return;
        console.innerHTML = '<span style="display:block;font-family:Inter,sans-serif;font-size:10px;font-weight:600;color:var(--text-muted);letter-spacing:2px;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border-color);">CONSOLE OUTPUT</span>';
        logs.slice(-50).forEach(log => {
            const div = document.createElement('div');
            div.className = 'console-line';
            div.textContent = log;
            console.appendChild(div);
        });
        console.scrollTop = console.scrollHeight;
    }

    let pollInterval = null;

    function startPolling() {
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(refreshStatus, 2000);
    }

    // ── INIT ──
    refreshStatus();

    // Auto-refresh cookies count
    document.addEventListener('DOMContentLoaded', () => {
        const cookies = document.getElementById('cookies');
        if (cookies) {
            const lines = cookies.value.trim().split('\\n').filter(l => l.trim());
            document.getElementById('cookieCount').textContent = lines.length + ' cookie sets loaded';
        }
    });

    document.getElementById('cookies')?.addEventListener('input', function() {
        const lines = this.value.trim().split('\\n').filter(l => l.trim());
        document.getElementById('cookieCount').textContent = lines.length + ' cookie sets loaded";
    });
</script>

</body>
</html>
"""

@app.route('/')
def index():
    config = db.get_user_config('MAIN')
    import datetime
    now = datetime.datetime.now().strftime("%H:%M:%S")
    return render_template_string(HTML_TEMPLATE, config=config, time=now)

# ── API ROUTES ──

@app.route('/api/get-config')
def api_get_config():
    config = db.get_user_config('MAIN')
    return jsonify({"success": True, "config": config})

@app.route('/api/save-config', methods=['POST'])
def api_save_config():
    data = request.json
    config = db.get_user_config('MAIN')
    db.update_user_config(
        'MAIN',
        data.get('chat_id', config['chat_id']),
        data.get('name_prefix', config['name_prefix']),
        data.get('delay', config['delay']),
        config.get('cookies', ''),
        data.get('messages', config['messages'])
    )
    return jsonify({"success": True})

@app.route('/api/save-cookies', methods=['POST'])
def api_save_cookies():
    data = request.json
    cookies_text = data.get('cookies', '')
    config = db.get_user_config('MAIN')
    parsed = parse_cookies_multi(cookies_text)
    db.update_user_config(
        'MAIN',
        config['chat_id'],
        config['name_prefix'],
        config['delay'],
        cookies_text,
        config['messages']
    )
    return jsonify({"success": True, "count": len(parsed)})

@app.route('/api/parse-cookies', methods=['POST'])
def api_parse_cookies():
    data = request.json
    cookies_text = data.get('cookies', '')
    parsed = parse_cookies_multi(cookies_text)
    return jsonify({
        "success": True,
        "count": len(parsed),
        "sets": [json.dumps(p) if isinstance(p, dict) else str(p) for p in parsed[:10]]
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    if auto_state.running:
        return jsonify({"success": False, "error": "Already running"})

    config = db.get_user_config('MAIN')
    if not config or not config.get('chat_id'):
        return jsonify({"success": False, "error": "Chat ID not set"})

    auto_state.running = True
    auto_state.stop_flag = False
    auto_state.message_count = 0
    db.set_automation_running('MAIN', True)

    thread = threading.Thread(target=run_automation_with_notification, args=(config,))
    thread.daemon = True
    thread.start()

    return jsonify({"success": True})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    auto_state.running = False
    auto_state.stop_flag = True
    db.set_automation_running('MAIN', False)
    return jsonify({"success": True})

@app.route('/api/status')
def api_status():
    config = db.get_user_config('MAIN')
    return jsonify({
        "success": True,
        "running": auto_state.running,
        "message_count": auto_state.message_count,
        "chat_id": config.get('chat_id', ''),
        "logs": auto_state.logs[-50:]
    })

# ── MAIN ──
if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║        HENRY'X - E2EE TOOL v3.0     ║
    ║     Offline Automation System        ║
    ╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
