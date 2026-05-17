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
    """Główna funkcja wstrzykująca Premium CSS i obsługująca suwaki przez zmienne."""
    bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
    bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

    local_css_string = """
    /* UKRYWANIE ELEMENTÓW SYSTEMOWYCH STREAMLIT */
    [data-testid="stHeader"] { background-color: transparent !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    .stDeployButton { display: none !important; }

    /* TŁO I MGŁA NA GŁÓWNYM EKRANIE */
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
        z-index: 0 !important; pointer-events: none !important; 
    }

    /* ========================================= */
    /* 🔥 NAPRAWA CZYTELNOŚCI FORMULARZY I TEKSTÓW */
    /* ========================================= */
    
    /* Wymuszenie jasnych etykiet we WSZYSTKICH modułach (Data, Selectbox, Input) */
    div[data-testid="stForm"] label p,
    div[data-testid="stTextInput"] label p,
    div[data-testid="stSelectbox"] label p,
    div[data-testid="stDateInput"] label p,
    div[data-testid="stTimeInput"] label p,
    div[data-testid="stNumberInput"] label p,
    div[data-testid="stTextArea"] label p {
        color: #cbd5e1 !important; /* Jasnoszary */
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
    }

    /* Wyodrębnienie bloków formularzy szkłem */
    div[data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
    }

    /* Wymuszenie czytelności nagłówków w głównym oknie (np. zakładki, tytuły) */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important; 
    }
    
    /* Poprawa koloru pomocniczego tekstu w elementach st.info, st.warning */
    .stAlert p { color: #f8fafc !important; }

    /* ========================================= */
    /* 🔥 BEZKOMPROMISOWY CIEMNY SIDEBAR 🔥      */
    /* ========================================= */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #0f172a !important; 
        background-image: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: transparent !important;
        background-image: radial-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px) !important;
        background-size: 16px 16px !important;
    }
    
    [data-testid="stSidebar"] * { color: #f8fafc !important; }

    .sidebar-header { 
        background: -webkit-linear-gradient(45deg, #60a5fa, #f8fafc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 1.6rem !important; font-weight: 900 !important; padding: 1.5rem 1rem 0.5rem 1rem !important;
    }
    
    .sidebar-subheader { 
        font-size: 0.85rem !important; color: #94a3b8 !important; 
        padding: 0 1rem 1.2rem 1rem !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; 
    }

    /* INTERAKTYWNE MENU RADIOWE */
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }

    div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important; padding: 14px 18px !important; margin: 6px 1rem !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    div[role="radiogroup"] > label:hover { 
        background: rgba(255, 255, 255, 0.08) !important; transform: translateX(8px) !important;
    }
    div[role="radiogroup"] > label[data-checked="true"] { 
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.05)) !important;
        border-left: 4px solid #3b82f6 !important; transform: translateX(8px) !important;
    }
    div[role="radiogroup"] > label p { 
        font-size: 1rem !important; font-weight: 500 !important; margin-left: 5px !important; 
    }

    /* SUWAKI USTAWIEŃ UI */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 12px !important; margin: 1rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary { background-color: transparent !important; }

    /* PRZYCISK WYLOGUJ */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #ef4444 !important; background-image: none !important;
        border: 1px solid #ef4444 !important; border-radius: 12px !important;
        padding: 12px !important; margin-top: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2) !important;
    }
    section[data-testid="stSidebar"] .stButton > button p, 
    section[data-testid="stSidebar"] .stButton > button div, 
    section[data-testid="stSidebar"] .stButton > button span {
        color: #ffffff !important; font-weight: 800 !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #dc2626 !important; border: 1px solid #dc2626 !important;
    }

    /* ========================================= */
    /* KARTY DASHBOARDU / MAGAZYNU               */
    /* ========================================= */
    .card-container { 
        background: rgba(30, 41, 59, 0.8) !important; border-radius: 15px !important; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important; padding: 20px !important; 
        margin-bottom: 15px !important; border: 1px solid rgba(255,255,255,0.08) !important; 
    }
    .card-value { font-size: 2.4rem !important; font-weight: bold !important; color: #f8fafc !important; }
    .card-title, .dashboard-title { color: #f8fafc !important; }
    .card-date-pill { color: #cbd5e1 !important; }
    .dashboard-subheader { color: #94a3b8 !important; }

    """

    local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
    local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(opacity))
    local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(blur))
    st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)
