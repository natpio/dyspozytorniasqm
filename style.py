import streamlit as st
import base64

def get_base64_of_bin_file(bin_file):
    """Odczytuje plik graficzny z dysku i zamienia go na format Base64 dla CSS."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def zastosuj_style(opacity, blur):
    """Główna funkcja wstrzykująca Premium CSS dla interfejsu SQM OS (bez paska bocznego)."""
    bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
    bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

    local_css_string = """
    /* ========================================= */
    /* 🚫 CAŁKOWITE USUNIĘCIE ELEMENTÓW SYSTEMU   */
    /* ========================================= */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    header { visibility: hidden !important; height: 0px !important; }
    [data-testid="stHeader"] { background-color: transparent !important; visibility: hidden !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    .stDeployButton { display: none !important; }

    /* ========================================= */
    /* 🌌 INTEGRACJA TŁA I POWŁOKA GLASSMORPHISM */
    /* ========================================= */
    .stApp {
        background-image: url("BACKGROUND_URL_PLACEHOLDER") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(15, 23, 42, OPACITY_PLACEHOLDER) !important; 
        backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important; 
        -webkit-backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important;
        z-index: 0 !important; pointer-events: none !important; 
    }

    /* ========================================= */
    /* 🔐 BEZPIECZNY KONTENER LOGOWANIA          */
    /* ========================================= */
    .login-container {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.95)) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 28px !important;
        padding: 40px !important;
        box-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.9) !important;
        margin-top: 10vh;
    }

    /* ========================================= */
    /* 🔥 TRÓJWYMIAROWE KAFELKI Z DANYMI LIVE   */
    /* ========================================= */
    div[data-testid="stButton"] button {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01)) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 24px !important;
        padding: 35px 20px !important;
        height: 150px !important;
        color: #f8fafc !important;
        font-size: 1.3rem !important;
        font-weight: 900 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        white-space: pre-wrap !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1.5 !important;
        text-align: center !important;
    }
    
    /* Efekt podświetlenia oraz uniesienia przy najechaniu kursem */
    div[data-testid="stButton"] button:hover {
        transform: translateY(-6px) scale(1.02) !important;
        background: linear-gradient(145deg, rgba(56, 189, 248, 0.25), rgba(59, 130, 246, 0.15)) !important;
        border-color: rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 20px 40px rgba(56, 189, 248, 0.3) !important;
        color: #ffffff !important;
    }

    /* Wizualna odpowiedź na kliknięcie (fizyka wciskania przycisku) */
    div[data-testid="stButton"] button:active {
        transform: translateY(-2px) scale(0.99) !important;
    }
    
    /* ⚡ SPERSONALIZOWANY PRZYCISK WYLOGOWANIA (TOP-BAR) ⚡ */
    div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] button {
        padding: 10px !important; 
        border-radius: 14px !important; 
        font-size: 1.1rem !important;
        height: auto !important;
        background: rgba(239, 68, 68, 0.15) !important; 
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        box-shadow: none !important;
    }
    div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] button:hover {
        background: rgba(239, 68, 68, 0.8) !important;
        border-color: #ef4444 !important;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* ========================================= */
    /* 📊 ARCHITEKTURA KART WEWNĘTRZNYCH        */
    /* ========================================= */
    .card-container { 
        background: rgba(30, 41, 59, 0.6) !important; 
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 20px !important; 
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3) !important; 
        padding: 22px !important; 
        margin-bottom: 15px !important; 
        border: 1px solid rgba(255, 255, 255, 0.08) !important; 
    }
    .card-value { font-size: 2.6rem !important; font-weight: 900 !important; color: #f8fafc !important; }
    .dashboard-title { color: #f8fafc !important; font-weight: 800 !important; }
    .dashboard-subheader { color: #94a3b8 !important; }

    .card-container.wszystkie-zlecenia { border-left: 6px solid #3b82f6 !important; }
    .card-container.nowe { border-left: 6px solid #f59e0b !important; }
    .card-container.w-trakcie { border-left: 6px solid #10b981 !important; }
    .card-container.zakonczone { border-left: 6px solid #8b5cf6 !important; }

    /* Estetyczne dostosowanie zakładek (Tabs) */
    .stTabs [data-testid="stVerticalBlock"] {
        background: rgba(15, 23, 42, 0.35) !important;
        padding: 24px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(8px) !important;
    }
    """

    local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
    local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(opacity))
    local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(blur))
    st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)
