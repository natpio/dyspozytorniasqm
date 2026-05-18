import streamlit as st
import base64

@st.cache_data
def get_base64_of_bin_file(bin_file):
    """Odczytuje plik graficzny z dysku i zamienia go na format Base64 dla CSS."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def zastosuj_style(opacity, blur):
    """Główna funkcja wstrzykująca Premium CSS i obsługująca suwaki przez zmienne."""
    bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
    bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

    local_css_string = """
    /* ========================================= */
    /* 🚫 UKRYWANIE ELEMENTÓW SYSTEMOWYCH        */
    /* ========================================= */
    [data-testid="stHeader"] { background-color: transparent !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    .stDeployButton { display: none !important; }

    /* ========================================= */
    /* 🌌 TŁO I MGŁA NA GŁÓWNYM EKRANIE         */
    /* ========================================= */
    .stApp {
        background-image: url("BACKGROUND_URL_PLACEHOLDER") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    /* Globalne, ciemne tło (Glassmorphism) */
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(15, 23, 42, OPACITY_PLACEHOLDER) !important; 
        backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important; 
        -webkit-backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important;
        z-index: -1 !important; /* Gwarancja z-index: -1, tło ląduje POD spodem aplikacji */
        pointer-events: none !important; 
    }

    /* ========================================= */
    /* 🎛️ LEWY PANEL: HUD (CONTROL TOWER)        */
    /* ========================================= */
    .hud-wrapper {
        background: rgba(30, 41, 59, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 22px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
        margin-bottom: 20px !important;
    }

    .hud-section-title {
        font-size: 0.8rem !important;
        color: #94a3b8 !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-bottom: 15px !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
        padding-bottom: 8px !important;
    }

    .hud-metric-container {
        display: flex !important;
        gap: 12px !important;
        margin-bottom: 25px !important;
    }

    .hud-metric-card {
        flex: 1 !important;
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 15px 10px !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }
    
    .hud-metric-card h5 {
        font-size: 0.65rem !important;
        color: #94a3b8 !important;
        margin: 0 0 8px 0 !important;
        text-transform: uppercase !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
    }

    .hud-metric-card h4 {
        font-size: 1.8rem !important;
        color: #f8fafc !important;
        margin: 0 !important;
        font-weight: 900 !important;
    }

    .border-blue { border-top: 4px solid #3b82f6 !important; }
    .border-green { border-top: 4px solid #10b981 !important; }
    .border-orange { border-top: 4px solid #f59e0b !important; }

    /* TOP-BAR SYSTEMOWY */
    .system-brand {
        font-size: 1.4rem; font-weight: 900; color: #f8fafc; letter-spacing: -0.5px;
        display: flex; align-items: center; gap: 10px;
    }
    .system-status-pill {
        background: rgba(56, 189, 248, 0.2); color: #38bdf8; font-size: 0.75rem; 
        padding: 4px 10px; border-radius: 12px; font-weight: 700; border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .system-clock {
        text-align: center; font-family: monospace; font-size: 1.1rem; color: #94a3b8;
        background: rgba(15, 23, 42, 0.5); padding: 8px 20px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05);
        display: inline-block; margin: 0 auto;
    }
    .system-user-tag {
        text-align: right; color: #cbd5e1; font-size: 0.95rem; display: flex; align-items: center; justify-content: flex-end; height: 100%;
    }
    .system-divider {
        height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); margin: 20px 0 30px 0;
    }

    /* ========================================= */
    /* 🔥 NAPRAWA CZYTELNOŚCI FORMULARZY         */
    /* ========================================= */
    div[data-testid="stForm"] label p,
    div[data-testid="stTextInput"] label p,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stDateInput"] label p,
    div[data-testid="stTimeInput"] label p,
    div[data-testid="stNumberInput"] label p,
    div[data-testid="stTextArea"] label p {
        color: #cbd5e1 !important; font-weight: 600 !important; font-size: 0.95rem !important; letter-spacing: 0.3px !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] div,
    div[data-baseweb="textarea"] textarea { color: #f8fafc !important; }

    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.6) !important; backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 16px !important;
        padding: 25px !important; box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
    }

    h1, h2, h3, h4, h5, h6 { color: #f8fafc !important; }
    .stAlert p { color: #f8fafc !important; }

    /* ========================================= */
    /* INTERAKTYWNE MENU RADIOWE (BŁYSKAWICZNE)  */
    /* ========================================= */
    div[data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child { 
        position: absolute !important; opacity: 0 !important; width: 0px !important; height: 0px !important; margin: 0 !important; padding: 0 !important; pointer-events: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] { display: flex !important; flex-direction: column !important; gap: 8px !important; width: 100% !important; }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background: rgba(255, 255, 255, 0.03) !important; border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important; padding: 14px 15px !important; margin: 0 !important; width: 100% !important;
        cursor: pointer !important; transition: background 0.2s ease, border 0.2s ease !important; display: flex !important; align-items: center !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover { background: rgba(255, 255, 255, 0.08) !important; }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.25), rgba(56, 189, 248, 0.05)) !important;
        border-color: rgba(56, 189, 248, 0.5) !important; border-left: 5px solid #38bdf8 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] p {
        color: #f8fafc !important; font-weight: 600 !important; font-size: 1.05rem !important; margin: 0 !important; margin-left: 5px !important; transition: transform 0.2s ease !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover p { transform: translateX(4px) !important; }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p { color: #38bdf8 !important; font-weight: 800 !important; }

    /* ========================================= */
    /* SUWAKI USTAWIEŃ UI                        */
    /* ========================================= */
    [data-testid="stExpander"] {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 12px !important; margin-top: 1rem !important;
    }
    [data-testid="stExpander"] summary { background-color: transparent !important; }

    /* ========================================= */
    /* KARTY DASHBOARDU / MAGAZYNU               */
    /* ========================================= */
    .card-container { 
        background: rgba(30, 41, 59, 0.7) !important; border-radius: 15px !important; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important; padding: 20px !important; 
        margin-bottom: 15px !important; border: 1px solid rgba(255,255,255,0.08) !important; 
    }
    .card-value { font-size: 2.4rem !important; font-weight: bold !important; color: #f8fafc !important; }
    .card-title, .dashboard-title { color: #f8fafc !important; }
    .card-date-pill { color: #cbd5e1 !important; }
    .dashboard-subheader { color: #94a3b8 !important; }
    
    .dashboard-header { display: flex; align-items: center; gap: 15px; margin-bottom: 5px; }
    .dashboard-title-icon { font-size: 2.5rem; }
    .dashboard-title { font-size: 2rem; font-weight: 900; letter-spacing: -1px; }
    """

    local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
    local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(opacity))
    local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(blur))
    st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)
