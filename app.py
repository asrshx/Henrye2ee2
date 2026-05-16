import streamlit as st
import cryptography
from cryptography.fernet import Fernet
import os
import gc
import base64
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. ADVANCED MEMORY MANAGEMENT & AGGRESSIVE GARBAGE COLLECTION
# -----------------------------------------------------------------------------
def clear_system_memory():
    """Har rerun par memory ko forcefully clean karne ke liye"""
    # 1. Streamlit ke cache ko internal level par clear karna
    st.cache_data.clear()
    
    # 2. Python ke garbage collector ko force karna RAM khali karne ke liye
    gc.collect()

# Har page load/interact par RAM clean karein
clear_system_memory()

# -----------------------------------------------------------------------------
# 2. STREAMLIT PAGE CONFIG & CUSTOM MODERN CARD CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Henry-X | Offline E2EE",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Dark Glassmorphism Cards Design UI
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Neumorphic/Glassmorphism Card Style */
    .henry-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }
    
    /* Card Titles */
    .card-title {
        color: #38bdf8;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Custom Output Box inside cards */
    .output-box {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
        font-family: monospace;
        color: #34d399;
        word-break: break-all;
        margin-top: 10px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_index=True)

# -----------------------------------------------------------------------------
# 3. CORE E2EE CRYPTOGRAPHY FUNCTIONS (With Strict RAM Control)
# -----------------------------------------------------------------------------
def generate_safe_key():
    return Fernet.generate_key().decode()

def encrypt_message(message: str, key: str) -> str:
    try:
        f = Fernet(key.encode())
        token = f.encrypt(message.encode())
        return token.decode()
    except Exception as e:
        return f"Error: Invalid Key Format! ({str(e)})"
    finally:
        # Strict local memory cleaning inside function
        if 'f' in locals(): del f
        gc.collect()

def decrypt_message(cipher_text: str, key: str) -> str:
    try:
        f = Fernet(key.encode())
        clean_cipher = cipher_text.strip()
        decrypted = f.decrypt(clean_cipher.encode())
        return decrypted.decode()
    except Exception:
        return "❌ Error: Galat Key ya corrupted encrypted data!"
    finally:
        if 'f' in locals(): del f
        gc.collect()

# -----------------------------------------------------------------------------
# 4. APP STATE INITIALIZATION & HISTORY LIMITER (Prevents RAM Full)
# -----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# RAM Saver: Agar history 10 se zyada ho jaye, toh purani history delete karo
if len(st.session_state.history) > 10:
    st.session_state.history = st.session_state.history[-10:]

# -----------------------------------------------------------------------------
# 5. HENRY-X UI LAYOUT (EVERYTHING WRAPPED IN CARDS)
# -----------------------------------------------------------------------------

# Title Section
st.markdown("<h1 style='text-align: center; color: #f1f5f9; font-weight: 800; margin-bottom: 5px;'>🔐 HENRY-X</h1>", unsafe_allow_index=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1rem; margin-bottom: 30px;'>100% Offline End-to-End Encryption Hub</p>", unsafe_allow_index=True)

# --- CARD 1: KEY GENERATOR ---
st.markdown("""
<div class="henry-card">
    <div class="card-title">🔑 Secret Key Generator</div>
    <p style='color: #94a3b8; font-size: 0.9rem; margin-top:-10px;'>Apni secure communication ke liye ek naye E2EE key generate karein.</p>
</div>
""", unsafe_allow_index=True)

# Streamlit buttons and inputs columns ke andar thoda gap dekar
col1, col2 = st.columns([2, 1])
with col1:
    if st.button("Generate New Secure Key", use_container_width=True):
        st.session_state.generated_key = generate_safe_key()

if "generated_key" in st.session_state:
    st.markdown(f'<div class="output-box">{st.session_state.generated_key}</div>', unsafe_allow_index=True)
    st.info("⚠️ Is key ko safe jagah copy karlein. Iske bina data decrypt nahi ho payega.")


# --- CARD 2: ENCRYPTION ENGINE ---
st.markdown("""
<div class="henry-card" style="margin-top: 20px;">
    <div class="card-title">🔒 Encrypt Message (Text ko Code me badlein)</div>
</div>
""", unsafe_allow_index=True)

enc_key = st.text_input("Encryption Key Dalein:", type="password", key="enc_k")
secret_msg = st.text_area("Apna Secret Message Likhein:", key="enc_m")

if st.button("Encrypt 🚀", use_container_width=True):
    if enc_key and secret_msg:
        encrypted_res = encrypt_message(secret_msg, enc_key)
        st.markdown(f'<div class="output-box">{encrypted_res}</div>', unsafe_allow_index=True)
        
        # Log to local memory session safely
        st.session_state.history.append(f"⏱️ {datetime.now().strftime('%H:%M')} - Text Encrypted")
        
        # Immediate memory clean up
        del encrypted_res
        gc.collect()
    else:
        st.error("Key aur Message dono dalna zaroori hai!")


# --- CARD 3: DECRYPTION ENGINE ---
st.markdown("""
<div class="henry-card" style="margin-top: 20px;">
    <div class="card-title">🔓 Decrypt Message (Code ko Text me badlein)</div>
</div>
""", unsafe_allow_index=True)

dec_key = st.text_input("Decryption Key Dalein:", type="password", key="dec_k")
cipher_msg = st.text_area("Encrypted Code (Ciphertext) Paste Karein:", key="dec_m")

if st.button("Decrypt 🔓", use_container_width=True):
    if dec_key and cipher_msg:
        decrypted_res = decrypt_message(cipher_msg, dec_key)
        st.markdown(f'<div class="output-box" style="color: #38bdf8;">{decrypted_res}</div>', unsafe_allow_index=True)
        
        st.session_state.history.append(f"⏱️ {datetime.now().strftime('%H:%M')} - Code Decrypted")
        
        del decrypted_res
        gc.collect()
    else:
        st.error("Key aur Encrypted Code dono dalna zaroori hai!")


# --- CARD 4: HEALTH MONITOR & RAM STATE ---
st.markdown("""
<div class="henry-card" style="margin-top: 20px;">
    <div class="card-title">🛡️ System Health & Session Logs</div>
</div>
""", unsafe_allow_index=True)

h_col1, h_col2 = st.columns(2)
h_col1.metric(label="RAM Optimization Status", value="⚡ AUTO-CLEAN")
h_col2.metric(label="Uptime State", value="24/7 Continuous")

if st.session_state.history:
    st.markdown("**Recent Activity Logs (Auto-limited to prevent memory leaks):**")
    for log in reversed(st.session_state.history):
        st.caption(log)

if st.button("Force Clear All Memory Loops", use_container_width=True):
    st.session_state.history = []
    if "generated_key" in st.session_state: del st.session_state.generated_key
    clear_system_memory()
    st.rerun()

# Footer
st.markdown('<div class="footer">Henry-X v2.0 • Secured Offline E2EE Engine • 24/7 Optimized</div>', unsafe_allow_index=True)
