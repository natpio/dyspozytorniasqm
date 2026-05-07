import streamlit as st
import extra_streamlit_components as stx
from streamlit_autorefresh import st_autorefresh
import datetime
import ui_lukasz
import ui_dawid
import ui_magazyn
import database
import base64

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(layout="wide", page_title="SQM DISPATCH Dashboard")

# --- 2. OBSŁUGA CIASTECZEK ---
cookie_manager = stx.CookieManager(key="sqm_dispatch_pro_v16")

# --- 3. INICJALIZACJA SESJI ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

if "wybrane_konto" not in st.session_state:
    st.session_state["wybrane_konto"] = None

if "blokada_autologowania" not in st.session_state:
    st.session_state["blokada_autologowania"] = False

# --- 4. LOGIKA LOGOWANIA / WYLOGOWANIA ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")

# Autologowanie 
if zalogowany_cookie and st.session_state["zalogowany"] is None and not st.session_state["blokada_autologowania"]:
    st.session_state["zalogowany"] = zalogowany_cookie
    op, bl = database.pobierz_ustawienia_uzytkownika(zalogowany_cookie)
    # BEZPIECZNIKI: Zabezpieczamy wartości przed błędem StreamlitValueAboveMaxError
    st.session_state.bg_opacity = max(0.0, min(1.0, float(op)))
    st.session_state.bg_blur = max(0, min(20, int(bl)))

# Domyślne wartości UI
if "bg_opacity" not in st.session_state:
    st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state:
    st.session_state.bg_blur = 4

def zapisz_zmiany_ui():
    if st.session_state["zalogowany"]:
        database.zapisz_ustawienia_uzytkownika(
            st.session_state["zalogowany"], 
            st.session_state.bg_opacity, 
            st.session_state.bg_blur
        )

# --- 5. OBSŁUGA TŁA ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

# --- 6. AGRESYWNY I LUKSUSOWY KOD CSS ---
local_css_string = """
/* UKRYWANIE ZNAKÓW WODNYCH STREAMLIT */
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* TŁO APLIKACJI I MGŁA */
.stApp {
    background-image: url("BACKGROUND_URL_PLACEHOLDER") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}
.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background-color: rgba(247, 249, 252, OPACITY_PLACEHOLDER) !important; 
    backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important; 
    -webkit-backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important;
    z-index: 0 !important;
    pointer-events: none !important; 
}

/* KONTENER GŁÓWNY */
.appview-container, .main {
    position: relative !important;
    z-index: 1 !important;
}

/* ========================================= */
/* 🔥 PREMIUM SIDEBAR 🔥                     */
/* ========================================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #1f2937 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * { color: #f8fafc !important; }

.sidebar-header { 
    font-size: 1.6rem !important; 
    font-weight: 900 !important; 
    padding: 1.5rem 1rem 0.5rem 1rem !important; 
    letter-spacing: 1px !important;
}
.sidebar-subheader { 
    font-size: 0.85rem !important; 
    color: #94a3b8 !important; 
    padding: 0 1rem 1.5rem 1rem !important; 
    border-bottom: 1px solid rgba(255,255,255,0.05) !important; 
    margin-bottom: 1rem !important; 
}

/* 🔥 INTERAKTYWNE MENU RADIOWE 🔥 */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }

div[role="radiogroup"] > label {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    padding: 12px 15px !important;
    margin: 8px 1rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    display: flex !important;
    align-items: center !important;
}
div[role="radiogroup"] > label:hover { 
    background: rgba(255, 255, 255, 0.08) !important; 
    transform: translateX(5px) !important;
}
div[role="radiogroup"] > label[data-checked="true"] { 
    background: rgba(93, 156, 236, 0.15) !important;
    border-left: 4px solid #5d9cec !important;
    border-top: 1px solid rgba(93, 156, 236, 0.3) !important;
    border-right: 1px solid rgba(93, 156, 236, 0.3) !important;
    border-bottom: 1px solid rgba(93, 156, 236, 0.3) !important;
    transform: translateX(5px) !important;
}
div[role="radiogroup"] > label p { 
    font-size: 1rem !important; 
    margin-left: 10px !important; 
    font-weight: 500 !important;
    white-space: nowrap !important;
}
div[role="radiogroup"] > label[data-checked="true"] p { 
    font-weight: 800 !important; 
    text-shadow: 0 0 8px rgba(93, 156, 236, 0.4) !important; 
}

/* 🔥 NAPRAWA EXPANDERA "Ustawienia UI" 🔥 */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {
    background-color: transparent !important;
}

/* PRZYCISK WYLOGOWANIA */
div[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    padding: 12px !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2) !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, #f87171 0%, #dc2626 100%) !important;
}

/* ========================================= */
/* 🔥 KARTY DASHBOARDU 🔥                    */
/* ========================================= */
.dashboard-header { display: flex !important; align-items: center !important; margin-bottom: 0.5rem !important; }
.dashboard-title-icon { font-size: 1.8rem !important; margin-right: 10px !important; }
.dashboard-title { font-size: 1.8rem !important; font-weight: bold !important; }
.dashboard-subheader { font-size: 0.9rem !important; margin-bottom: 2rem !important; }

.card-container { 
    background: white !important; 
    border-radius: 15px !important; 
    box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important; 
    padding: 20px !important; 
    display: flex !important; 
    justify-content: space-between !important; 
    align-items: center !important; 
    margin-bottom: 15px !important; 
    border: 1px solid #e2e8f0 !important; 
}
.card-info { display: flex !important; flex-direction: column !important; }
.card-title { font-size: 0.9rem !important; color: #64748b !important; margin-bottom: 5px !important; }
.card-value { font-size: 2.4rem !important; font-weight: bold !important; color: #0f172a !important; }
.card-date-pill { display: flex !important; align-items: center !important; border-radius: 15px !important; padding: 4px 12px !important; font-size: 0.75rem !important; margin-top: 5px !important; font-weight: bold !important; }
.card-icon { font-size: 2.8rem !important; opacity: 0.9 !important; }

.nowe .card-date-pill { background-color: rgba(230, 126, 34, 0.1) !important; color: #e67e22 !important; }
.w-trakcie .card-date-pill { background-color: rgba(241, 196, 15, 0.1) !important; color: #f1c40f !important; }
.zakonczone .card-date-pill { background-color: rgba(39, 174, 96, 0.1) !important; color: #27ae60 !important; }
.wszystkie-zlecenia .card-date-pill { background-color: rgba(93, 156, 236, 0.1) !important; color: #5d9cec !important; }

.table-header { font-size: 1.1rem !important; font-weight: bold !important; margin-top: 2rem !important; margin-bottom: 1rem !important; }
.dataframe { border-radius: 10px !important; overflow: hidden !important; box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important; background-color: white !important; }

/* ======================================================== */
/* 🌙 ADAPTACJA DO CIEMNEGO MOTYWU PRZEGLĄDARKI (DARK MODE) */
/* ======================================================== */
@media (prefers-color-scheme: dark) {
    .stApp::before { background-color: rgba(15, 23, 42, OPACITY_PLACEHOLDER) !important; }
    .appview-container, .main { color: #f8fafc !important; }
    .dashboard-title { color: #f8fafc !important; }
    .dashboard-subheader { color: #94a3b8 !important; }
    
    .card-container {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
    }
    .card-title { color: #94a3b8 !important; }
    .card-value { color: #f8fafc !important; }
    .table-header { color: #f8fafc !important; }
    .dataframe { background-color: rgba(30, 41, 59, 0.8) !important; border-color: #334155 !important; }
    
    div[style*="color: #0f172a"] { color: #f8fafc !important; }
    div[style*="background: white"] { background: transparent !important; }
}
"""

local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(st.session_state.bg_opacity))
local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(st.session_state.bg_blur))
st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)

# --- 7. EKRAN LOGOWANIA ---
if st.session_state["zalogowany"] is None:
    st.markdown('<div class="dashboard-header"><span style="font-size:2rem;">🔐</span><span class="dashboard-title" style="margin-left:10px;">SQM DISPATCH</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Wybierz konto, aby się zalogować:</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👨‍💼\n\nŁukasz", use_container_width=True, key="sel_l"): 
            st.session_state["wybrane_konto"] = "Łukasz"
    with c2:
        if st.button("🚛\n\nDawid", use_container_width=True, key="sel_d"): 
            st.session_state["wybrane_konto"] = "Dawid"
    with c3:
        if st.button("🏭\n\nMagazyn", use_container_width=True, key="sel_m"): 
            st.session_state["wybrane_konto"] = "Magazyn"
    
    if st.session_state["wybrane_konto"]:
        st.markdown(f"<br>Logowanie do: **{st.session_state['wybrane_konto']}**", unsafe_allow_html=True)
        pin = st.text_input("Podaj PIN", type="password")
        if st.button("Zaloguj", type="primary", use_container_width=True):
            key = st.session_state["wybrane_konto"].lower().replace("ł", "l")
            if pin == str(st.secrets["passwords"][key]):
                st.session_state["zalogowany"] = st.session_state["wybrane_konto"]
                st.session_state["blokada_autologowania"] = False 
                
                # Zapis ciasteczka na 30 dni
                waznosc = datetime.datetime.now() + datetime.timedelta(days=30)
                cookie_manager.set("zalogowany", st.session_state["zalogowany"], expires_at=waznosc)
                
                # Wczytanie UI
                op, bl = database.pobierz_ustawienia_uzytkownika(st.session_state["zalogowany"])
                # BEZPIECZNIKI
                st.session_state.bg_opacity = max(0.0, min(1.0, float(op)))
                st.session_state.bg_blur = max(0, min(20, int(bl)))
                
                st.rerun()
            else:
                st.error("Błędny PIN!")

# --- 8. PANEL GŁÓWNY ---
else:
    uzytkownik = st.session_state["zalogowany"]
    with st.sidebar:
        st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Zalogowano jako: {uzytkownik}</div>', unsafe_allow_html=True)
        
        if uzytkownik == "Łukasz":
            wybor = st.radio("M", ["⚙️ Dashboard", "➕ Nowy Wpis", "🏭 Logistyka", "🛠️ Konsola Admin.", "📂 Archiwum"], label_visibility="collapsed")
        elif uzytkownik == "Dawid":
            wybor = st.radio("M", ["📱 Moje Zlecenia"], label_visibility="collapsed")
        else:
            wybor = st.radio("M", ["🏭 Tablica Magazynowa"], label_visibility="collapsed")

        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
        
        if uzytkownik == "Łukasz":
            with st.expander("🛠️ Ustawienia UI"):
                st.slider("Krycie", 0.0, 1.0, step=0.05, key="bg_opacity", on_change=zapisz_zmiany_ui)
                st.slider("Rozmycie", 0, 20, step=1, key="bg_blur", on_change=zapisz_zmiany_ui)

        # BEZPIECZNE WYLOGOWANIE
        if st.button("Wyloguj się", use_container_width=True, type="primary"):
            try:
                cookie_manager.delete("zalogowany")
            except KeyError:
                pass 
                
            st.session_state["zalogowany"] = None
            st.session_state["wybrane_konto"] = None
            st.session_state["blokada_autologowania"] = True
            st.rerun()

    # ROUTING
    if uzytkownik == "Łukasz":
        st_autorefresh(interval=30000, key="refresh_l")
        if wybor == "⚙️ Dashboard": ui_lukasz.pokaz_dashboard()
        elif wybor == "➕ Nowy Wpis": ui_lukasz.pokaz_formularz()
        elif wybor == "🏭 Logistyka": ui_lukasz.pokaz_magazyn()
        elif wybor == "🛠️ Konsola Admin.": ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📂 Archiwum": ui_lukasz.pokaz_archiwum()
    elif uzytkownik == "Dawid":
        ui_dawid.pokaz_panel()
    else:
        st_autorefresh(interval=30000, key="refresh_m")
        ui_magazyn.pokaz_tablice()
