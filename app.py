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

# --- 2. OBSŁUGA CIASTECZEK (Logowanie na 30 dni) ---
cookie_manager = stx.CookieManager(key="cookie_manager_sqm_v3")

# --- 3. INICJALIZACJA SESJI I DANYCH UI ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

if "wybrane_konto" not in st.session_state:
    st.session_state["wybrane_konto"] = None

# Automatyczne logowanie z ciasteczka (tylko jeśli nie jesteśmy w trakcie wylogowywania)
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")
if zalogowany_cookie and st.session_state["zalogowany"] is None:
    st.session_state["zalogowany"] = zalogowany_cookie
    # Wczytujemy osobiste ustawienia tła
    op, bl = database.pobierz_ustawienia_uzytkownika(zalogowany_cookie)
    st.session_state.bg_opacity = op
    st.session_state.bg_blur = bl

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

# --- 4. OBSŁUGA PLIKU TŁA ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

# --- 5. PEŁNY KOD CSS (White Label + Naprawa Czcionek + Metryki) ---
local_css_string = """
/* UKRYWANIE ELEMENTÓW SYSTEMOWYCH */
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* DYNAMICZNE TŁO */
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
    background-color: rgba(247, 249, 252, OPACITY_PLACEHOLDER); 
    backdrop-filter: blur(BLUR_PLACEHOLDERpx); 
    -webkit-backdrop-filter: blur(BLUR_PLACEHOLDERpx); 
    z-index: 0;
    pointer-events: none; 
}

/* KONTENER GŁÓWNY */
.appview-container, .main { position: relative; z-index: 1; color: #0f172a; }

/* STYLIZACJA PASKA BOCZNEGO - BIAŁA CZCIONKA */
section[data-testid="stSidebar"] {
    background-color: #1a2233 !important;
    color: #ffffff !important;
    padding-top: 1rem;
    z-index: 100;
}
section[data-testid="stSidebar"] * { color: #ffffff !important; }

.sidebar-header { font-size: 1.3rem; font-weight: bold; color: white; padding: 0 1rem; }
.sidebar-subheader { font-size: 0.8rem; color: #8da1b3 !important; padding: 0.2rem 1rem 1rem 1rem; border-bottom: 1px solid #3d495f; margin-bottom: 1rem; }
.sidebar-menu-header { font-size: 0.75rem; color: #8da1b3 !important; padding: 0 1rem; margin-top: 1rem; text-transform: uppercase; }

/* PRZYCISKI MENU BOCZNEGO */
div[role="radiogroup"] > label {
    display: flex;
    align-items: center;
    padding: 10px 1rem;
    cursor: pointer;
    border-radius: 8px;
    margin: 4px 0.5rem;
    transition: background-color 0.2s;
}
div[role="radiogroup"] > label:hover { background-color: #2b3a53; }
div[role="radiogroup"] > label[data-checked="true"] { background-color: #2b3a53; }
div[role="radiogroup"] > label[data-checked="true"] p { color: #5d9cec !important; font-weight: bold !important; }
div[role="radiogroup"] > label span[data-baseweb="radio"] div:first-child { display: none !important; }
div[role="radiogroup"] > label p { font-size: 0.95rem; margin-left: 10px; color: #ffffff !important; }

/* PRZYCISK WYLOGOWANIA */
div[data-testid="stSidebar"] .stButton > button {
    background-color: #8e44ad !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: bold !important;
    padding: 12px;
    width: 100%;
}

/* KARTY DASHBOARDU - PRZYWRÓCENIE LAYOUTU */
.card-container { background: linear-gradient(145deg, #ffffff, #f8fafc); border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); padding: 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border: 1px solid #e2e8f0; }
.card-info { display: flex; flex-direction: column; }
.card-title { font-size: 0.85rem; color: #64748b; margin-bottom: 5px; }
.card-value { font-size: 2.1rem; font-weight: bold; color: #0f172a; margin-bottom: 10px; }
.card-date-pill { display: flex; align-items: center; border-radius: 15px; padding: 4px 10px; font-size: 0.7rem; }
.card-icon { font-size: 2.5rem; opacity: 0.8; }
"""

local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(st.session_state.bg_opacity))
local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(st.session_state.bg_blur))
st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)

# --- 6. EKRAN LOGOWANIA ---
if st.session_state["zalogowany"] is None:
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🔐</span><span class="dashboard-title">SQM DISPATCH</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader" style="color: #64748b; margin-bottom: 2rem;">Wybierz konto i podaj PIN.</div>', unsafe_allow_html=True)
    
    # 3 Duże Przyciski do wyboru konta
    col_l, col_d, col_m = st.columns(3)
    
    with col_l:
        if st.button("👨‍💼\n\nŁukasz", use_container_width=True, key="sel_lukasz"):
            st.session_state["wybrane_konto"] = "Łukasz"
    with col_d:
        if st.button("🚛\n\nDawid", use_container_width=True, key="sel_dawid"):
            st.session_state["wybrane_konto"] = "Dawid"
    with col_m:
        if st.button("🏭\n\nMagazyn", use_container_width=True, key="sel_magazyn"):
            st.session_state["wybrane_konto"] = "Magazyn"
    
    # Jeśli konto wybrane, pokaż pole PIN
    if st.session_state["wybrane_konto"]:
        st.markdown(f"### Logowanie: **{st.session_state['wybrane_konto']}**")
        col_pin, _ = st.columns([1, 2])
        with col_pin:
            pin = st.text_input("Podaj PIN", type="password", key="input_pin")
            if st.button("Zaloguj", type="primary", use_container_width=True):
                secret_key = st.session_state["wybrane_konto"].lower().replace("ł", "l")
                if pin == str(st.secrets["passwords"][secret_key]):
                    st.session_state["zalogowany"] = st.session_state["wybrane_konto"]
                    waznosc = datetime.datetime.now() + datetime.timedelta(days=30)
                    cookie_manager.set("zalogowany", st.session_state["zalogowany"], expires_at=waznosc)
                    op, bl = database.pobierz_ustawienia_uzytkownika(st.session_state["zalogowany"])
                    st.session_state.bg_opacity, st.session_state.bg_blur = op, bl
                    st.rerun()
                else:
                    st.error("Błędny PIN!")

# --- 7. INTERFEJS PO ZALOGOWANIU ---
else:
    uzytkownik = st.session_state["zalogowany"]
    
    with st.sidebar:
        st.markdown(f'<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Zalogowano jako: {uzytkownik}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-menu-header">MENU GŁÓWNE</div>', unsafe_allow_html=True)
        
        if uzytkownik == "Łukasz":
            wybor = st.radio("Nav", ["⚙️ Dashboard", "➕ Nowy Wpis", "🏭 Logistyka Magazynowa", "🛠️ Konsola Administracyjna", "📂 Archiwum Cyfrowe"], label_visibility="collapsed")
        elif uzytkownik == "Dawid":
            wybor = st.radio("Nav", ["📱 Moje Zlecenia"], label_visibility="collapsed")
        elif uzytkownik == "Magazyn":
            wybor = st.radio("Nav", ["🏭 Tablica Magazynowa"], label_visibility="collapsed")

        st.markdown("<div style='min-height: 35vh;'></div>", unsafe_allow_html=True)
        
        if uzytkownik == "Łukasz":
            with st.expander("🛠️ Ustawienia UI"):
                st.slider("Krycie tła", 0.0, 1.0, step=0.05, key="bg_opacity", on_change=zapisz_zmiany_ui)
                st.slider("Rozmycie (Blur)", 0, 20, step=1, key="bg_blur", on_change=zapisz_zmiany_ui)

        # NAPRAWA WYLOGOWANIA
        if st.button("Wyloguj się", use_container_width=True, key="logout_btn"):
            cookie_manager.delete("zalogowany")
            st.session_state["zalogowany"] = None
            st.session_state["wybrane_konto"] = None
            st.rerun()

    # --- 8. ROUTING ---
    if uzytkownik == "Łukasz":
        st_autorefresh(interval=30000, key="refresh_lukasz")
        if wybor == "⚙️ Dashboard": ui_lukasz.pokaz_dashboard()
        elif wybor == "➕ Nowy Wpis": ui_lukasz.pokaz_formularz()
        elif wybor == "🏭 Logistyka Magazynowa": ui_lukasz.pokaz_magazyn()
        elif wybor == "🛠️ Konsola Administracyjna": ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📂 Archiwum Cyfrowe": ui_lukasz.pokaz_archiwum()
            
    elif uzytkownik == "Dawid":
        ui_dawid.pokaz_panel()

    elif uzytkownik == "Magazyn":
        st_autorefresh(interval=30000, key="refresh_magazyn")
        ui_magazyn.pokaz_tablice()
