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
cookie_manager = stx.CookieManager(key="sqm_dispatch_v10_darkmode")

# --- 3. INICJALIZACJA SESJI ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

if "wybrane_konto" not in st.session_state:
    st.session_state["wybrane_konto"] = None

if "blokada_autologowania" not in st.session_state:
    st.session_state["blokada_autologowania"] = False

# --- 4. LOGIKA LOGOWANIA / WYLOGOWANIA ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")

# Automatyczne logowanie z ciasteczka (Zabezpieczone flagą)
if zalogowany_cookie and st.session_state["zalogowany"] is None and not st.session_state["blokada_autologowania"]:
    st.session_state["zalogowany"] = zalogowany_cookie
    # Wczytujemy ustawienia UI z bazy
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

# --- 6. PEŁNY KOD CSS (JASNY I CIEMNY MOTYW) ---
local_css_string = """
/* UKRYWANIE ELEMENTÓW SYSTEMOWYCH */
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* DOMYŚLNE TŁO I BIAŁA MGŁA (TRYB JASNY) */
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
.appview-container, .main {
    position: relative;
    z-index: 1;
    color: #0f172a;
}

/* PASEK BOCZNY - ZAWSZE CIEMNY */
section[data-testid="stSidebar"] {
    background-color: #1a2233 !important;
    color: #ffffff !important;
    padding-top: 1rem;
}
section[data-testid="stSidebar"] * { color: #ffffff !important; }

.sidebar-header { font-size: 1.4rem; font-weight: bold; padding: 1rem; }
.sidebar-subheader { font-size: 0.85rem; color: #8da1b3 !important; padding: 0 1rem 1rem 1rem; border-bottom: 1px solid #3d495f; margin-bottom: 1rem; }

/* PRZYCISKI MENU */
div[role="radiogroup"] > label {
    display: flex;
    align-items: center;
    padding: 12px 1rem;
    cursor: pointer;
    border-radius: 10px;
    margin: 5px 0.5rem;
}
div[role="radiogroup"] > label:hover { background-color: #2b3a53; }
div[role="radiogroup"] > label[data-checked="true"] { background-color: #2b3a53; }
div[role="radiogroup"] > label[data-checked="true"] p { color: #5d9cec !important; font-weight: bold !important; }
div[role="radiogroup"] > label span[data-baseweb="radio"] { display: none !important; }
div[role="radiogroup"] > label p { font-size: 1rem; margin-left: 10px; color: #ffffff !important;}

/* PRZYCISK WYLOGOWANIA (CZERWONY) */
div[data-testid="stSidebar"] .stButton > button {
    background-color: #ef4444 !important;
    color: white !important;
    border: none !important;
    padding: 12px !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    width: 100%;
    transition: background-color 0.2s;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #dc2626 !important;
}

/* KARTY DASHBOARDU (DOMYŚLNIE JASNE) */
.dashboard-header { display: flex; align-items: center; margin-bottom: 0.5rem; }
.dashboard-title-icon { font-size: 1.8rem; margin-right: 10px; color: #8da1b3; }
.dashboard-title { font-size: 1.8rem; font-weight: bold; color: #0f172a; }
.dashboard-subheader { font-size: 0.9rem; color: #64748b; margin-bottom: 2rem; }

.card-container { background: white !important; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); padding: 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border: 1px solid #e2e8f0; }
.card-info { display: flex; flex-direction: column; }
.card-title { font-size: 0.9rem; color: #64748b; margin-bottom: 5px; }
.card-value { font-size: 2.2rem; font-weight: bold; color: #0f172a; }
.card-date-pill { display: flex; align-items: center; border-radius: 15px; padding: 4px 12px; font-size: 0.75rem; margin-top: 10px; }
.card-icon { font-size: 2.8rem; opacity: 0.9; }

.nowe .card-date-pill { background-color: rgba(230, 126, 34, 0.1); color: #e67e22; }
.w-trakcie .card-date-pill { background-color: rgba(241, 196, 15, 0.1); color: #f1c40f; }
.zakonczone .card-date-pill { background-color: rgba(39, 174, 96, 0.1); color: #27ae60; }
.wszystkie-zlecenia .card-date-pill { background-color: rgba(93, 156, 236, 0.1); color: #5d9cec; }

.table-header { font-size: 1.1rem; font-weight: bold; color: #0f172a; margin-top: 2rem; margin-bottom: 1rem; }
.dataframe { border-radius: 10px !important; overflow: hidden !important; box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important; background-color: white !important; }

/* ======================================================== */
/* 🌙 ADAPTACJA DO CIEMNEGO MOTYWU PRZEGLĄDARKI (DARK MODE) */
/* ======================================================== */
@media (prefers-color-scheme: dark) {
    /* 1. Mroczna mgła zamiast białej */
    .stApp::before {
        background-color: rgba(15, 23, 42, OPACITY_PLACEHOLDER) !important;
    }

    /* 2. Główne teksty aplikacji i nagłówki na jasnoszare */
    .appview-container, .main { color: #f8fafc !important; }
    .dashboard-title { color: #f8fafc !important; }
    .dashboard-subheader { color: #94a3b8 !important; }

    /* 3. Ciemne karty z efektem szkła dla metryk */
    .card-container {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95)) !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
    }
    .card-title { color: #94a3b8 !important; }
    .card-value { color: #f8fafc !important; }

    /* 4. Ciemne tabele */
    .table-header { color: #f8fafc !important; }
    .dataframe { background-color: rgba(30, 41, 59, 0.8) !important; border-color: #334155 !important; }

    /* 5. Inteligentne nadpisywanie sztywnych czarnych kolorów z innych plików (np. ui_magazyn) */
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
    st.markdown('<div class="dashboard-subheader">Wybierz konto:</div>', unsafe_allow_html=True)
    
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
                st.session_state.bg_opacity, st.session_state.bg_blur = op, bl
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
            wybor = st.radio("M", ["⚙️ Dashboard", "➕ Nowy Wpis", "🏭 Logistyka Magazynowa", "🛠️ Konsola Administracyjna", "📂 Archiwum Cyfrowe"], label_visibility="collapsed")
        elif uzytkownik == "Dawid":
            wybor = st.radio("M", ["📱 Moje Zlecenia"], label_visibility="collapsed")
        else:
            wybor = st.radio("M", ["🏭 Tablica Magazynowa"], label_visibility="collapsed")

        st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
        
        if uzytkownik == "Łukasz":
            with st.expander("🛠️ Ustawienia UI"):
                st.slider("Krycie", 0.0, 1.0, step=0.05, key="bg_opacity", on_change=zapisz_zmiany_ui)
                st.slider("Rozmycie", 0, 20, step=1, key="bg_blur", on_change=zapisz_zmiany_ui)

        # BEZPIECZNE WYLOGOWANIE
        if st.button("Wyloguj się", use_container_width=True, type="primary"):
            try:
                cookie_manager.delete("zalogowany")
            except KeyError:
                pass # Ignorujemy błąd, jeśli ciasteczko już nie istnieje
                
            st.session_state["zalogowany"] = None
            st.session_state["wybrane_konto"] = None
            st.session_state["blokada_autologowania"] = True
            st.rerun()

    # ROUTING
    if uzytkownik == "Łukasz":
        st_autorefresh(interval=30000, key="refresh_l")
        if wybor == "⚙️ Dashboard": ui_lukasz.pokaz_dashboard()
        elif wybor == "➕ Nowy Wpis": ui_lukasz.pokaz_formularz()
        elif wybor == "🏭 Logistyka Magazynowa": ui_lukasz.pokaz_magazyn()
        elif wybor == "🛠️ Konsola Administracyjna": ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📂 Archiwum Cyfrowe": ui_lukasz.pokaz_archiwum()
    elif uzytkownik == "Dawid":
        ui_dawid.pokaz_panel()
    else:
        st_autorefresh(interval=30000, key="refresh_m")
        ui_magazyn.pokaz_tablice()
