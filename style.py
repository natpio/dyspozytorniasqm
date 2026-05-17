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
    """Główna funkcja wstrzykująca Premium CSS dla pełnoekranowej architektury Control Tower."""
    bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
    bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

    local_css_string = """
    /* ========================================= */
    /* 🚫 INTEGRALNE OCZYSZCZANIE INTERFEJSU     */
    /* ========================================= */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    header { visibility: hidden !important; height: 0px !important; }
    [data-testid="stHeader"] { background-color: transparent !important; visibility: hidden !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    .stDeployButton { display: none !important; }
    
    /* Wycięcie standardowych marginesów bocznych Streamlita dla pełnego ekranu OS */
    .block-container {
        padding-top: 15px !important;
        padding-bottom: 10px !important;
        padding-left: 25px !important;
        padding-right: 25px !important;
        max-width: 100% !important;
    }

    /* ========================================= */
    /* 🌌 INTEGRACJA CYFROWEGO TŁA OS             */
    /* ========================================= */
    .stApp {
        background-image: url("BACKGROUND_URL_PLACEHOLDER") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(10, 15, 30, OPACITY_PLACEHOLDER) !important; 
        backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important; 
        -webkit-backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important;
        z-index: 0 !important; pointer-events: none !important; 
    }

    /* ========================================= */
    /* 📟 SPERSONALIZOWANE SYSTEMOWE MENU HUD     */
    /* ========================================= */
    .system-brand {
        font-size: 1.4rem; font-weight: 900; color: #f8fafc; letter-spacing: -0.5px; padding-top: 5px;
    }
    .system-status-pill {
        background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4);
        color: #38bdf8; font-size: 0.7rem; padding: 2px 8px; border-radius: 8px; vertical-align: middle; margin-left: 5px;
    }
    .system-clock {
        text-align: center; color: #64748b; font-family: monospace; font-size: 1.1rem; padding-top: 8px; font-weight: bold;
    }
    .system-user-tag {
        text-align: right; color: #94a3b8; padding-top: 8px; font-size: 1rem;
    }
    .system-divider {
        border-top: 1px solid rgba(255, 255, 255, 0.08); margin-top: 10px; margin-bottom: 20px;
    }

    /* ========================================= */
    /* 🔥 NAPRAWA MENU (RADIO) - KONTRAST I WYGLĄD */
    /* ========================================= */
    /* Całkowite ukrycie szarych kółek od st.radio */
    .stRadio div[role="radiogroup"] div[data-baseweb="radio"] > div:first-child { 
        display: none !important; 
    }
    
    .stRadio div[role="radiogroup"] { 
        display: flex; flex-direction: column; gap: 8px; width: 100%; 
    }
    .stRadio div[role="radiogroup"] label { 
        width: 100% !important; margin: 0 !important; cursor: pointer !important; 
    }
    
    /* Główne tło i domyślny wygląd przycisku w menu */
    .stRadio div[role="radiogroup"] label div[data-baseweb="radio"] > div:last-child {
        width: 100% !important; 
        display: flex !important; 
        align-items: center !important;
        padding: 12px 18px !important; 
        background: rgba(255, 255, 255, 0.08) !important; /* Wyraźniejsze tło dla nieaktywnych */
        border-radius: 12px !important; 
        color: #f8fafc !important; /* BIAŁY TEKST dla mocnego kontrastu */
        font-size: 1.05rem !important;
        font-weight: 600 !important; 
        border: 1px solid rgba(255,255,255,0.1) !important; 
        transition: all 0.2s ease !important;
    }
    
    /* Wymuszenie białego koloru na tekście wewnątrz Streamlita */
    .stRadio div[role="radiogroup"] label div[data-baseweb="radio"] > div:last-child p { 
        color: inherit !important; 
        font-weight: inherit !important;
        text-align: left !important; 
        margin: 0 !important; 
    }
    
    /* Hover (Najazd myszką) */
    .stRadio div[role="radiogroup"] label:hover div[data-baseweb="radio"] > div:last-child {
        background: rgba(255, 255, 255, 0.15) !important; 
        color: #ffffff !important; 
        transform: translateX(4px);
    }
    
    /* Zaznaczony (Aktywny moduł) */
    .stRadio div[role="radiogroup"] label:has(input:checked) div[data-baseweb="radio"] > div:last-child {
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.25), rgba(56, 189, 248, 0.05)) !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important; 
        color: #38bdf8 !important; 
        border-left: 5px solid #38bdf8 !important;
        font-weight: 800 !important;
    }

    /* ========================================= */
    /* STRUKTURA PANELU HUD (LEWA STRONA)        */
    /* ========================================= */
    .hud-wrapper {
        background: rgba(15, 23, 42, 0.4) !important; backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important; border-radius: 24px !important;
        padding: 25px !important; box-shadow: 0 20px 45px rgba(0,0,0,0.4) !important;
    }
    /* Jaśniejsze nagłówki sekcji w lewym panelu */
    .hud-section-title {
        font-size: 0.8rem; font-weight: 800; color: #cbd5e1 !important; letter-spacing: 1px; margin-bottom: 15px; text-transform: uppercase;
    }

    /* KARTY METRYK W PANELU HUD */
    .hud-metric-container { display: flex; gap: 10px; justify-content: space-between; width: 100%; }
    .hud-metric-card {
        background: rgba(255, 255, 255, 0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important; padding: 12px 8px !important; text-align: center; flex: 1;
    }
    .hud-metric-card h5 { margin: 0 0 5px 0 !important; color: #94a3b8 !important; font-size: 0.65rem !important; font-weight: 800; }
    .hud-metric-card h4 { margin: 0 !important; color: #f8fafc !important; font-size: 1.6rem !important; font-weight: 900; }
    
    .hud-metric-card.border-blue { border-left: 4px solid #3b82f6 !important; }
    .hud-metric-card.border-green { border-left: 4px solid #10b981 !important; }
    .hud-metric-card.border-orange { border-left: 4px solid #f59e0b !important; }

    /* STRUKTURA VIEWPORTU (PRAWA STRONA - MODUŁY) */
    .viewport-wrapper {
        background: rgba(15, 23, 42, 0.2) !important; backdrop-filter: blur(5px) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important; border-radius: 24px !important;
        padding: 20px !important; box-shadow: inset 0 0 40px rgba(0,0,0,0.2) !important;
    }

    /* SPECJALISTYCZNY WYLOGUJ (TOP-BAR) */
    div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] button {
        padding: 6px !important; border-radius: 12px !important; font-size: 1.1rem !important; height: auto !important;
        background: rgba(239, 68, 68, 0.15) !important; border: 1px solid rgba(239, 68, 68, 0.4) !important; color: #ef4444 !important;
    }
    div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] button:hover {
        background: #ef4444 !important; color: white !important; box-shadow: 0 0 15px rgba(239, 68, 68, 0.5) !important; transform: translateY(-1px);
    }

    /* KARTY WEWNĘTRZNE (DLA MODUŁÓW) */
    .card-container { 
        background: rgba(22, 30, 49, 0.75) !important; backdrop-filter: blur(10px) !important;
        border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.06) !important; padding: 20px !important; margin-bottom: 15px !important;
    }
    .card-value { font-size: 2.4rem !important; font-weight: 900 !important; color: #f8fafc !important; }
    .dashboard-title { color: #f8fafc !important; font-weight: 800 !important; }
    .dashboard-subheader { color: #94a3b8 !important; }

    /* WZORCOWE DOSTOSOWANIE FORMULARZY I ZAKŁADEK */
    .stTabs [data-testid="stVerticalBlock"] {
        background: rgba(15, 23, 42, 0.4) !important; padding: 20px !important; border-radius: 16px !important; border: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    
    /* MODALNE OKNA INTERFEJSU MAPY LUB KALENDARZA */
    iframe { border-radius: 16px !important; box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important; }
    """

    local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
    local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(opacity))
    local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(blur))
    st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)
