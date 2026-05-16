import streamlit as st
import base64

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f: data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def zastosuj_style(opacity, blur):
    bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
    bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

    local_css_string = """
    /* UKRYWANIE ELEMENTÓW SYSTEMOWYCH STREAMLIT (Całkowite usunięcie sidebara) */
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    header { visibility: hidden !important; height: 0px !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }

    /* GLOBALNE TŁO GLASSMORPHISM */
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

    /* KONTENER LOGOWANIA */
    .login-container {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.95)) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 28px !important;
        padding: 40px !important;
        box-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.9) !important;
        margin-top: 10vh;
    }

    /* ========================================= */
    /* POTĘŻNE KAFELKI MENU (Dashboard)          */
    /* ========================================= */
    div[data-testid="stButton"] button {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01)) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 24px !important;
        padding: 30px 15px !important;
        height: auto !important;
        color: #f8fafc !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        white-space: pre-wrap !important; /* Pozwala na użycie znaku nowej linii w przycisku */
    }
    
    div[data-testid="stButton"] button:hover {
        transform: translateY(-5px) scale(1.02) !important;
        background: linear-gradient(145deg, rgba(56, 189, 248, 0.2), rgba(59, 130, 246, 0.1)) !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 20px 40px rgba(56, 189, 248, 0.2) !important;
        color: #ffffff !important;
    }
    
    /* Mniejszy przycisk wylogowania na top-barze */
    div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] button {
        padding: 5px !important; border-radius: 12px !important; font-size: 1rem !important;
        background: rgba(239, 68, 68, 0.2) !important; border-color: rgba(239, 68, 68, 0.5) !important;
    }
    div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] button:hover {
        background: rgba(239, 68, 68, 0.8) !important;
    }

    /* KARTY DASHBOARDU (Z ui_lukasz) */
    .card-container { 
        background: rgba(30, 41, 59, 0.7) !important; backdrop-filter: blur(10px);
        border-radius: 20px !important; box-shadow: 0 8px 30px rgba(0,0,0,0.3) !important; 
        padding: 20px !important; margin-bottom: 15px !important; border: 1px solid rgba(255,255,255,0.08) !important; 
    }
    .card-value { font-size: 2.4rem !important; font-weight: 900 !important; color: #f8fafc !important; }
    .dashboard-title { color: #f8fafc !important; }
    """

    local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
    local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(opacity))
    local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(blur))
    st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)
