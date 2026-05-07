import streamlit as st
from streamlit_autorefresh import st_autorefresh
import ui_lukasz
import ui_dawid
import database
import base64

# 1. KONFIGURACJA STRONY (Musi być na samym początku)
st.set_page_config(layout="wide", page_title="SQM DISPATCH Dashboard")

# 2. INICJALIZACJA ZMIENNYCH SESYJNYCH
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

# Domyślne wartości UI (zostaną nadpisane z bazy danych po zalogowaniu)
if "bg_opacity" not in st.session_state:
    st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state:
    st.session_state.bg_blur = 4

# 3. FUNKCJA POMOCNICZA: ZAPIS USTAWIEŃ DO BAZY
def zapisz_zmiany_ui():
    """Wysyła aktualne wartości suwaków bezpośrednio do Google Sheets"""
    if st.session_state["zalogowany"]:
        database.zapisz_ustawienia_uzytkownika(
            st.session_state["zalogowany"], 
            st.session_state.bg_opacity, 
            st.session_state.bg_blur
        )

# 4. FUNKCJA DO ŁADOWANIA OBRAZU TŁA
def get_base64_of_bin_file(bin_file):
    """Konwertuje obraz na format tekstowy dla CSS"""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Zakoduj plik tlolukasz2.png do Base64
bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')
bg_img_url = f"data:image/png;base64,{bg_img_base64}" if bg_img_base64 else ""

# 5. PEŁNY KOD CSS (White Label + Dynamiczne Tło + Menu)
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

/* STYLIZACJA PASKA BOCZNEGO */
section[data-testid="stSidebar"] {
    background-color: #1a2233 !important;
    color: #ffffff !important;
    padding-top: 1rem;
    z-index: 100;
}

.sidebar-header { font-size: 1.2rem; font-weight: bold; padding: 0 1rem 1rem 1rem; border-bottom: 1px solid #3d495f; margin-bottom: 1rem; color: white; }
.sidebar-subheader { font-size: 0.8rem; color: #8da1b3 !important; padding: 0 1rem 1.5rem 1rem; }
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

/* STOPKA PASKA BOCZNEGO */
.sidebar-footer-text { 
    color: #8da1b3 !important; 
    font-size: 0.75rem; 
    border-top: 1px solid #3d495f; 
    padding-top: 15px; 
    margin-bottom: 5px; 
}
"""

# Podmiana dynamicznych wartości w CSS
local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(st.session_state.bg_opacity))
local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(st.session_state.bg_blur))

st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)

# 6. EKRAN LOGOWANIA
if st.session_state["zalogowany"] is None:
    st.markdown('<h2 style="color: #1a2233;">🔐 SQM DISPATCH - Logowanie</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b;">Podaj swój kod PIN, aby uzyskać dostęp.</p>', unsafe_allow_html=True)
    
    col1, _ = st.columns([1, 3])
    with col1:
        pin = st.text_input("Kod PIN", type="password")
        if st.button("Zaloguj", type="primary", use_container_width=True):
            imie = None
            if pin == "1234": imie = "Łukasz"
            elif pin == "5678": imie = "Dawid"
            
            if imie:
                st.session_state["zalogowany"] = imie
                # WCZYTYWANIE USTAWIEŃ OSOBISTYCH Z BAZY
                op, bl = database.pobierz_ustawienia_uzytkownika(imie)
                st.session_state.bg_opacity = op
                st.session_state.bg_blur = bl
                st.rerun()
            else:
                st.error("Błędny PIN!")

# 7. INTERFEJS PO ZALOGOWANIU
else:
    uzytkownik = st.session_state["zalogowany"]
    
    with st.sidebar:
        st.markdown(f'<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Zalogowano jako: {uzytkownik}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-menu-header">MENU</div>', unsafe_allow_html=True)
        
        # Nawigacja zależna od uprawnień
        if uzytkownik == "Łukasz":
            wybor = st.radio("Nawigacja", [
                "⚙️ Dashboard", 
                "➕ Nowy Wpis", 
                "🏭 Logistyka Magazynowa", 
                "🛠️ Konsola Administracyjna", 
                "📂 Archiwum Cyfrowe"
            ], label_visibility="collapsed")
        else:
            wybor = st.radio("Nawigacja", ["📱 Moje Zlecenia"], label_visibility="collapsed")

        # Pchnięcie stopki na dół
        st.markdown("<div style='min-height: 25vh;'></div>", unsafe_allow_html=True)
        
        # STOPKA PASKA BOCZNEGO
        st.markdown(f'<div class="sidebar-footer-text">SQM DISPATCH<br>Zalogowano jako: {uzytkownik}</div>', unsafe_allow_html=True)
        
        # UKRYTE USTAWIENIA UI (Tylko dla Łukasza)
        if uzytkownik == "Łukasz":
            with st.expander("🛠️ Ukryte Ustawienia UI"):
                st.markdown("<small>Dostosuj widoczność i rozmycie tła.</small>", unsafe_allow_html=True)
                st.slider("Gęstość mgły", 0.0, 1.0, step=0.05, key="bg_opacity", on_change=zapisz_zmiany_ui)
                st.slider("Siła rozmycia", 0, 20, step=1, key="bg_blur", on_change=zapisz_zmiany_ui)

        # PRZYCISK WYLOGOWANIA
        if st.button("Wyloguj się", use_container_width=True, type="secondary"):
            st.session_state["zalogowany"] = None
            st.rerun()

    # 8. ROUTING - WYWOŁYWANIE MODUŁÓW
    if uzytkownik == "Łukasz":
        st_autorefresh(interval=30000, limit=None, key="odswiezanie_lukasz")
        
        if wybor == "⚙️ Dashboard":
            ui_lukasz.pokaz_dashboard()
        elif wybor == "➕ Nowy Wpis":
            ui_lukasz.pokaz_formularz()
        elif wybor == "🏭 Logistyka Magazynowa":
            ui_lukasz.pokaz_magazyn()
        elif wybor == "🛠️ Konsola Administracyjna":
            ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📂 Archiwum Cyfrowe":
            ui_lukasz.pokaz_archiwum()
            
    elif uzytkownik == "Dawid":
        ui_dawid.pokaz_panel()
