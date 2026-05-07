import streamlit as st
import extra_streamlit_components as stx
from streamlit_autorefresh import st_autorefresh
import datetime
import ui_lukasz
import ui_dawid
import ui_magazyn
import database
import base64

# --- 1. KONFIGURACJA STRONY (Musi być na samej górze) ---
st.set_page_config(layout="wide", page_title="SQM DISPATCH Dashboard")

# --- 2. OBSŁUGA CIASTECZEK (Logowanie na 30 dni) ---
# Używamy unikalnego klucza, aby uniknąć konfliktów przy odświeżaniu
cookie_manager = stx.CookieManager(key="sqm_dispatch_cookie_manager_v4")

# --- 3. INICJALIZACJA ZMIENNYCH SESYJNYCH ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

if "wybrane_konto" not in st.session_state:
    st.session_state["wybrane_konto"] = None

# Automatyczne logowanie z ciasteczka (jeśli użytkownik nie jest w trakcie wylogowywania)
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")
if zalogowany_cookie and st.session_state["zalogowany"] is None:
    st.session_state["zalogowany"] = zalogowany_cookie
    # Wczytujemy osobiste ustawienia tła z bazy danych
    op, bl = database.pobierz_ustawienia_uzytkownika(zalogowany_cookie)
    st.session_state.bg_opacity = op
    st.session_state.bg_blur = bl

# Domyślne wartości UI (jeśli brak rekordów w bazie)
if "bg_opacity" not in st.session_state:
    st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state:
    st.session_state.bg_blur = 4

# Funkcja pomocnicza do zapisu zmian UI
def zapisz_zmiany_ui():
    if st.session_state["zalogowany"]:
        database.zapisz_ustawienia_uzytkownika(
            st.session_state["zalogowany"], 
            st.session_state.bg_opacity, 
            st.session_state.bg_blur
        )

# --- 4. FUNKCJA DO ŁADOWANIA OBRAZU TŁA ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

# --- 5. PEŁNY KOD CSS (White Label + Tło + Sidebar + Karty) ---
local_css_string = """
/* UKRYWANIE ELEMENTÓW SYSTEMOWYCH STREAMLIT */
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* DYNAMICZNE TŁO Z EFEKTEM MROŻONEGO SZKŁA */
.stApp {
    background-image: url("BACKGROUND_URL_PLACEHOLDER") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    background-color: #f7f9fc !important; 
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

/* STYLIZACJA PASKA BOCZNEGO - WYMUSZONA BIAŁA CZCIONKA */
section[data-testid="stSidebar"] {
    background-color: #1a2233 !important;
    color: #ffffff !important;
    padding-top: 1rem;
    z-index: 100;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

.sidebar-header { font-size: 1.3rem; font-weight: bold; color: white; padding: 0 1rem; }
.sidebar-subheader { font-size: 0.8rem; color: #8da1b3 !important; padding: 0.2rem 1rem 1rem 1rem; border-bottom: 1px solid #3d495f; margin-bottom: 1rem; }
.sidebar-menu-header { font-size: 0.75rem; color: #8da1b3 !important; padding: 0 1rem; margin-top: 1rem; text-transform: uppercase; }

/* PRZYCISKI MENU (RADIO) */
div[role="radiogroup"] > label {
    display: flex;
    align-items: center;
    padding: 10px 1rem;
    cursor: pointer;
    border-radius: 8px;
    margin: 4px 0.5rem;
    transition: background-color 0.2s;
    background-color: transparent;
}
div[role="radiogroup"] > label:hover { background-color: #2b3a53; }
div[role="radiogroup"] > label[data-checked="true"] { background-color: #2b3a53; }
div[role="radiogroup"] > label[data-checked="true"] p { color: #5d9cec !important; font-weight: bold !important; }
div[role="radiogroup"] > label span[data-baseweb="radio"] div:first-child { display: none !important; }
div[role="radiogroup"] > label p { font-size: 0.95rem; margin-left: 10px; color: #ffffff !important; }

/* PRZYCISK WYLOGOWANIA W PASKU BOCZNYM */
div[data-testid="stSidebar"] .stButton > button {
    background-color: #8e44ad !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: bold !important;
    transition: background-color 0.2s;
    padding: 10px 0 !important;
}
div[data-testid="stSidebar"] .stButton > button:hover { background-color: #732d91 !important; }

/* KARTY METRYK NA DASHBOARDZIE */
.dashboard-header { display: flex; align-items: center; margin-bottom: 0.5rem; }
.dashboard-title-icon { font-size: 1.8rem; margin-right: 10px; color: #8da1b3; }
.dashboard-title { font-size: 1.8rem; font-weight: bold; color: #0f172a; }
.dashboard-subheader { font-size: 0.9rem; color: #64748b; margin-bottom: 2rem; }

.card-container { background: linear-gradient(145deg, #ffffff, #f8fafc); border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); padding: 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; transition: transform 0.2s; border: 1px solid #e2e8f0; }
.card-container:hover { transform: translateY(-3px); }
.card-info { display: flex; flex-direction: column; }
.card-title { font-size: 0.85rem; color: #64748b; margin-bottom: 10px; }
.card-value { font-size: 2.2rem; font-weight: bold; color: #0f172a; margin-bottom: 15px; }
.card-date-pill { display: flex; align-items: center; border-radius: 15px; padding: 4px 10px; font-size: 0.75rem; }
.card-date-icon { margin-right: 5px; font-size: 0.8rem; }
.card-icon { font-size: 2.5rem; }

.nowe .card-date-pill { background-color: rgba(230, 126, 34, 0.1); color: #e67e22; }
.w-trakcie .card-date-pill { background-color: rgba(241, 196, 15, 0.1); color: #f1c40f; }
.zakonczone .card-date-pill { background-color: rgba(39, 174, 96, 0.1); color: #27ae60; }
.wszystkie-zlecenia .card-date-pill { background-color: rgba(93, 156, 236, 0.1); color: #5d9cec; }
"""

# Podmiana parametrów dynamicznych w CSS
local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(st.session_state.bg_opacity))
local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(st.session_state.bg_blur))

st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)

# --- 6. EKRAN LOGOWANIA (Z PRZYCISKAMI) ---
if st.session_state["zalogowany"] is None:
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🔐</span><span class="dashboard-title">SQM DISPATCH</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader" style="color: #64748b; margin-bottom: 2rem;">Wybierz konto, aby się zalogować.</div>', unsafe_allow_html=True)
    
    # Trzy duże przyciski do wyboru konta
    col_l, col_d, col_m = st.columns(3)
    
    with col_l:
        if st.button("👨‍💼\n\nŁukasz", use_container_width=True, key="btn_sel_lukasz"):
            st.session_state["wybrane_konto"] = "Łukasz"
    with col_d:
        if st.button("🚛\n\nDawid", use_container_width=True, key="btn_sel_dawid"):
            st.session_state["wybrane_konto"] = "Dawid"
    with col_m:
        if st.button("🏭\n\nMagazyn", use_container_width=True, key="btn_sel_magazyn"):
            st.session_state["wybrane_konto"] = "Magazyn"
            
    # Formularz wpisywania PINu po wyborze konta
    if st.session_state["wybrane_konto"]:
        st.markdown(f"### Logowanie jako: **{st.session_state['wybrane_konto']}**")
        col_pin, _ = st.columns([1, 2])
        with col_pin:
            pin = st.text_input("Podaj kod PIN", type="password", key="login_pin_input")
            if st.button("Zaloguj", type="primary", use_container_width=True):
                # Mapowanie nazwy na klucz w secrets (np. "Łukasz" -> "lukasz")
                secret_key = st.session_state["wybrane_konto"].lower().replace("ł", "l")
                
                try:
                    poprawne_haslo = str(st.secrets["passwords"][secret_key])
                except KeyError:
                    st.error("Hasło dla tego użytkownika nie jest skonfigurowane w systemie.")
                    st.stop()

                if pin == poprawne_haslo:
                    st.session_state["zalogowany"] = st.session_state["wybrane_konto"]
                    
                    # Ciasteczko na 30 dni
                    waznosc_ciastka = datetime.datetime.now() + datetime.timedelta(days=30)
                    cookie_manager.set("zalogowany", st.session_state["zalogowany"], expires_at=waznosc_ciastka)
                    
                    # Wczytujemy ustawienia tła z bazy danych
                    op, bl = database.pobierz_ustawienia_uzytkownika(st.session_state["zalogowany"])
                    st.session_state.bg_opacity = op
                    st.session_state.bg_blur = bl
                    st.rerun()
                else:
                    st.error("Nieprawidłowy kod PIN!")

# --- 7. INTERFEJS PO ZALOGOWANIU ---
else:
    uzytkownik = st.session_state["zalogowany"]
    
    with st.sidebar:
        # Nagłówek i (tylko raz!) status logowania
        st.markdown(f'<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Zalogowano jako: {uzytkownik}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-menu-header">MENU GŁÓWNE</div>', unsafe_allow_html=True)
        
        # Nawigacja zależna od uprawnień
        if uzytkownik == "Łukasz":
            wybor = st.radio("Nav", [
                "⚙️ Dashboard", 
                "➕ Nowy Wpis", 
                "🏭 Logistyka Magazynowa", 
                "🛠️ Konsola Administracyjna", 
                "📂 Archiwum Cyfrowe"
            ], label_visibility="collapsed")
        elif uzytkownik == "Dawid":
            wybor = st.radio("Nav", ["📱 Moje Zlecenia"], label_visibility="collapsed")
        elif uzytkownik == "Magazyn":
            wybor = st.radio("Nav", ["🏭 Tablica Magazynowa"], label_visibility="collapsed")

        # Rozpychacz (wypycha resztę elementów na dół paska bocznego)
        st.markdown("<div style='min-height: 35vh;'></div>", unsafe_allow_html=True)
        
        # Ustawienia UI (Tylko dla Łukasza) na samym dole
        if uzytkownik == "Łukasz":
            with st.expander("🛠️ Ustawienia UI"):
                st.markdown("<small style='color: #8da1b3;'>Dostosuj widoczność tła.</small>", unsafe_allow_html=True)
                st.slider("Gęstość mgły", 0.0, 1.0, step=0.05, key="bg_opacity", on_change=zapisz_zmiany_ui)
                st.slider("Siła rozmycia", 0, 20, step=1, key="bg_blur", on_change=zapisz_zmiany_ui)
                st.markdown("<br>", unsafe_allow_html=True)

        # PRZYCISK WYLOGOWANIA (Kasowanie ciasteczka i sesji)
        if st.button("Wyloguj się", use_container_width=True):
            cookie_manager.delete("zalogowany")
            st.session_state["zalogowany"] = None
            st.session_state["wybrane_konto"] = None
            st.rerun()

    # --- 8. ROUTING - MODUŁY ZEWNĘTRZNE ---
    if uzytkownik == "Łukasz":
        st_autorefresh(interval=30000, limit=None, key="odswiezanie_lukasz")
        if wybor == "⚙️ Dashboard": ui_lukasz.pokaz_dashboard()
        elif wybor == "➕ Nowy Wpis": ui_lukasz.pokaz_formularz()
        elif wybor == "🏭 Logistyka Magazynowa": ui_lukasz.pokaz_magazyn()
        elif wybor == "🛠️ Konsola Administracyjna": ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📂 Archiwum Cyfrowe": ui_lukasz.pokaz_archiwum()
            
    elif uzytkownik == "Dawid":
        ui_dawid.pokaz_panel()

    elif uzytkownik == "Magazyn":
        st_autorefresh(interval=30000, limit=None, key="odswiezanie_magazyn")
        ui_magazyn.pokaz_tablice()
