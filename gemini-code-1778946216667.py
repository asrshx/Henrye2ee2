import streamlit as st
from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import gc

# -----------------------------------------------------------------------------
# MEMORY & CLEANUP MANAGEMENT
# -----------------------------------------------------------------------------
def clear_memory():
    st.cache_data.clear()
    gc.collect()

clear_memory()

# -----------------------------------------------------------------------------
# PAGE CONFIG & CARDS UI DESIGN
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Henry-X Automation", page_icon="🤖", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    .henry-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .card-title { color: #38bdf8; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .status-box { background: #0f172a; border-left: 4px solid #34d399; padding: 10px; font-family: monospace; color: #34d399; }
</style>
""", unsafe_allow_index=True)

st.markdown("<h1 style='text-align: center;'>🤖 HENRY-X AUTOMATION</h1>", unsafe_allow_index=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>E2EE Text Generation + Facebook Auto Sender</p>", unsafe_allow_index=True)

# -----------------------------------------------------------------------------
# CORE LOGIC: SELENIUM MESSENGER INJECTOR
# -----------------------------------------------------------------------------
def fb_auto_sender(email, password, profile_url, encrypted_message, loop_count, delay):
    # Headless mode config (Background me chalne ke liye aur RAM bachane ke liye)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    status_placeholder = st.empty()
    
    try:
        status_placeholder.markdown("<div class='status-box'>🌐 Browser shuru ho raha hai...</div>", unsafe_allow_index=True)
        driver = webdriver.Chrome(options=chrome_options)
        
        # 1. Login to Facebook (Mobile version operates faster with less RAM)
        driver.get("https://mbasic.facebook.com")
        time.sleep(2)
        
        status_placeholder.markdown("<div class='status-box'>🔑 Logging into Facebook...</div>", unsafe_allow_index=True)
        driver.find_key = driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        time.sleep(4)
        
        # 2. Target User Ke Chat Page Par Jaana
        status_placeholder.markdown("<div class='status-box'>🎯 Target profile par ja rahe hain...</div>", unsafe_allow_index=True)
        driver.get(profile_url)
        time.sleep(3)
        
        # Message button dhoondhna (mbasic layout me "Message" link hota hai)
        try:
            msg_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Message")
            msg_button.click()
            time.sleep(3)
        except:
            # Agar direct link na mile toh direct messages URL par bhejna
            status_placeholder.markdown("<div class='status-box'>❌ Direct Message button nahi mila. Profile URL sahi check karein.</div>", unsafe_allow_index=True)
            driver.quit()
            return
        
        # 3. NON-STOP AUTOMATION LOOP
        for i in range(loop_count):
            # Message box dhoondhna aur text enter karna
            text_box = driver.find_element(By.NAME, "body")
            text_box.send_keys(encrypted_message)
            
            # Send button par click karna
            send_btn = driver.find_element(By.NAME, "Send")
            send_btn.click()
            
            status_placeholder.markdown(f"<div class='status-box'>✅ Message {i+1}/{loop_count} Bheja Gaya!</div>", unsafe_allow_index=True)
            time.sleep(delay) # Anti-ban delay
            
        status_placeholder.markdown("<div class='status-box'>🎉 Saare messages successfully bhej diye gaye! Connection closed.</div>", unsafe_allow_index=True)
        
    except Exception as e:
        status_placeholder.markdown(f"<div class='status-box' style='border-left-color: #f87171; color: #f87171;'>❌ Error: {str(e)}</div>", unsafe_allow_index=True)
    finally:
        if 'driver' in locals():
            driver.quit() # RAM khali karne ke liye browser har haal me close hoga
        clear_memory()

# -----------------------------------------------------------------------------
# UI CARDS LAYOUT
# -----------------------------------------------------------------------------

# CARD 1: ENCRYPTION
st.markdown("<div class='henry-card'><div class='card-title'>🔐 Step 1: Message ko E2EE Code me badlein</div></div>", unsafe_allow_index=True)
secret_key = st.text_input("Encryption Key (Fernet 32-byte Base64):", value="🚨 Apni Secure Key Yahan Dalein")
raw_text = st.text_area("Jo message automatic bhejna hai wo likhein:")

encrypted_payload = ""
if raw_text and secret_key:
    try:
        f = Fernet(secret_key.encode() if len(secret_key) >= 32 else Fernet.generate_key())
        encrypted_payload = f.encrypt(raw_text.encode()).decode()
        st.code(encrypted_payload, language="text")
    except:
        st.caption("Valid Fernet Key dalein ya fir text enter karein.")

# CARD 2: FB CREDENTIALS & TARGET
st.markdown("<div class='henry-card' style='margin-top:15px;'><div class='card-title'>👤 Step 2: Facebook Login Details & Target</div></div>", unsafe_allow_index=True)
fb_email = st.text_input("Facebook Email / Phone:")
fb_pass = st.text_input("Facebook Password:", type="password")
target_profile = st.text_input("Target Profile URL (e.g., https://mbasic.facebook.com/username):")

# CARD 3: AUTOMATION SETTINGS
st.markdown("<div class='henry-card' style='margin-top:15px;'><div class='card-title'>⚙️ Step 3: Automation Settings (Anti-Ban)</div></div>", unsafe_allow_index=True)
msg_limit = st.number_input("Kitne Messages Bhejne Hain? (Loop Count):", min_value=1, max_value=500, value=10)
msg_delay = st.slider("Har message ke beech ka gap (Seconds me):", min_value=1, max_value=20, value=3)

# START BUTTON
if st.button("🚀 Start Non-Stop Sending", use_container_width=True):
    if fb_email and fb_pass and target_profile and encrypted_payload:
        fb_auto_sender(fb_email, fb_pass, target_profile, encrypted_payload, msg_limit, msg_delay)
    else:
        st.error("Kripya saari details (Login, Target, aur Encrypted Message) sahi se bharein!")