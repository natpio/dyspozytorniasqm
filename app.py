import streamlit as st
from streamlit_autorefresh import st_autorefresh
import ui_lukasz
import ui_dawid
import base64 # Nowy import do obsługi pliku tła

# Konfiguracja strony musi być na samej górze
st.set_page_config(layout="wide", page_title="SQM DISPATCH Dashboard")

# Inicjalizacja sesji logowania
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

# --- FUNKCJA DO ŁADOWANIA OBRAZU TŁA ---
def get_base64_of_bin_file(bin_file):
    """Konwertuje plik binarny na format base64 dla CSS"""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Zakoduj plik tlolukasz2.png do Base64
bg_img_base64 = get_base64_of_bin_file('tlolukasz2.png')

# Przygotuj URL dla CSS
if bg_img_base64:
    bg_img_url = f"data:image/png;base64,{bg_img_base64}"
else:
    # Fallback, gdyby pliku nie było (np. błąd ścieżki na GitHubie)
    bg_img_url = "" 
    st.warning("⚠️ Nie znaleziono pliku 'tlolukasz2.png'. Używam tła zastępczego.")

# --- CSS Z AKTUALIZACJĄ TŁA NA PLIK 'tlolukasz2.png' ---
local_css_string = f"""
/* --- 1. UKRYWANIE ELEMENTÓW STREAMLITA (ZNAKI WODNE) --- */
[data-testid="stHeader"] {{ display: none !important; }}
footer {{ display: none !important; }}
#MainMenu {{ visibility: hidden !important; }}
.stDeployButton {{ display: none !important; }}

/* --- 2. NOWE TŁO Z PLIKU 'tlolukasz2.png' (Z EFEKTEM MROŻONEGO SZKŁA) --- */
/* Wymuszenie tła na głównym kontenerze aplikacji (.stApp) */
.stApp {{
    background-image: url("{bg_img_url}") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
    background-color: #f7f9fc !important; /* Fallback color */
}}

/* Nakładka "mrożonego szkła" dla wyciszenia tła i poprawy czytelności */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(247, 249, 252, 0.85); /* 85% przezroczystości, kolor chłodnej bieli */
    backdrop-filter: blur(2px); /* Delikatne rozmycie tekstury */
    z-index: -1;
}}

/* Globalny kolor tekstu - głęboki granat dla maksymalnej czytelności na teksturze */
.main {{
    color: #0f172a;
}}

/* --- 3. STYLIZACJA PASKA BOCZNEGO (Sidebar) --- */
section[data-testid="stSidebar"] {{
    background-color: #1a2233 !important;
    color: #ffffff !important;
    padding-top: 1rem;
}}
section[data-testid="stSidebar"] * {{
    color: #ffffff !important;
}

/* --- MAGIA CSS: Przerabiamy standardowe st.radio na Twoje przyciski --- */
div[role="radiogroup"] > label {{
    display: flex;
    align-items: center;
    padding: 10px 1rem;
    cursor: pointer;
    border-radius: 8px;
    margin: 4px 0.5rem;
    transition: background-color 0.2s;
    background-color: transparent;
}
div[role="radiogroup"] > label:hover {{
    background-color: #2b3a53;
}
/* Zaznaczona opcja */
div[role="radiogroup"] > label[data-checked="true"], 
div[role="radiogroup"] > label[aria-checked="true"] {{
    background-color: #2b3a53;
}
div[role="radiogroup"] > label[data-checked="true"] p, 
div[role="radiogroup"] > label[aria-checked="true"] p {{
    color: #5d9cec !important;
    font-weight: bold !important;
}
/* Ukrycie standardowego kółka radio */
div[role="radiogroup"] > label span[data-baseweb="radio"] div:first-child {{
    display: none !important;
}
/* Powiększenie tekstu w menu */
div[role="radiogroup"] > label p {{
    font-size: 0.95rem;
    margin-left: 10px;
}

/* Reszta Twoich klas (Karty, Nagłówki, Tabela) */
.sidebar-header {{ font-size: 1.2rem; font-weight: bold; padding: 0 1rem 1rem 1rem; border-bottom: 1px solid #3d495f; margin-bottom: 1rem; }}
.sidebar-subheader {{ font-size: 0.8rem; color: #8da1b3 !important; padding: 0 1rem 1.5rem 1rem; }}
.sidebar-menu-header {{ font-size: 0.75rem; color: #8da1b3 !important; padding: 0 1rem; margin-top: 1rem; text-transform: uppercase; }}

.dashboard-header {{ display: flex; align-items: center; margin-bottom: 0.5rem; }}
.dashboard-title-icon {{ font-size: 1.8rem; margin-right: 10px; color: #8da1b3; }}
.dashboard-title {{ font-size: 1.8rem; font-weight: bold; color: #333; }}
.dashboard-subheader {{ font-size: 0.9rem; color: #6c757d; margin-bottom: 2rem; }}

.card-container {{ background: linear-gradient(145deg, #ffffff, #e6e6e6); border-radius: 15px; box-shadow: 10px 10px 30px #e6e6e6, -10px -10px 30px #ffffff; padding: 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; transition: transform 0.2s; border: 1px solid #f1f5f9; }}
.card-container:hover {{ transform: translateY(-3px); }}
.card-info {{ display: flex; flex-direction: column; }}
.card-title {{ font-size: 0.85rem; color: #6c757d; margin-bottom: 10px; }}
.card-value {{ font-size: 2.2rem; font-weight: bold; color: #333; margin-bottom: 15px; }}
.card-date-pill {{ display: flex; align-items: center; border-radius: 15px; padding: 4px 10px; font-size: 0.75rem; }}
.card-date-icon {{ margin-right: 5px; font-size: 0.8rem; }}
.card-icon {{ font-size: 2.5rem; }}

.nowe .card-date-pill {{ background-color: rgba(230, 126, 34, 0.1); color: #e67e22; }}
.w-trakcie .card-date-pill {{ background-color: rgba(241, 196, 15, 0.1); color: #f1c40f; }}
.zakonczone .card-date-pill {{ background-color: rgba(39, 174, 96, 0.1); color: #27ae60; }}
.wszystkie-zlecenia .card-date-pill {{ background-color: rgba(93, 156, 236, 0.1); color: #5d9cec; }}

.table-header {{ font-size: 1.1rem; font-weight: bold; color: #333; margin-top: 2rem; margin-bottom: 1rem; }}
.dataframe {{ border-radius: 10px !important; overflow: hidden !important; box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important; background-color: white !important; }}

.sidebar-footer-login {{ position: fixed; bottom: 80px; left: 20px; color: #8da1b3 !important; font-size: 0.75rem; }}
"""
st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)

# --- EKRAN LOGOWANIA ---
if st.session_state["zalogowany"] is None:
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🔐</span><span class="dashboard-title">SQM DISPATCH</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Zaloguj się podając PIN.</div>', unsafe_allow_html=True)
    
    col1, _ = st.columns([1, 3])
    with col1:
        pin = st.text_input("Kod PIN", type="password")
        if st.button("Zaloguj", type="primary"):
            if pin == "1234":
                st.session_state["zalogowany"] = "Łukasz"
                st.rerun()
            elif pin == "5678":
                st.session_state["zalogowany"] = "Dawid"
                st.rerun()
            else:
                st.error("Błędny PIN!")

# --- PO ZALOGOWANIU ---
else:
    uzytkownik = st.session_state["zalogowany"]
    
    # --- PANEL BOCZNY (Sidebar) ---
    with st.sidebar:
        st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Zalogowano jako: {uzytkownik}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-menu-header">MENU</div>', unsafe_allow_html=True)
        
        # Nawigacja Pythonowa z ukrytymi radio buttonami przez CSS
        if uzytkownik == "Łukasz":
            wybor = st.radio("Nawigacja", [
                "⚙️ Dashboard", 
                "➕ Nowy Wpis", 
                "🏭 Logistyka Magazynowa", 
                "🛠️ Konsola Administracyjna", 
                "📂 Archiwum Cyfrowe"
            ], label_visibility="collapsed")
        elif uzytkownik == "Dawid":
            wybor = st.radio("Nawigacja", [
                "📱 Moje Zlecenia"
            ], label_visibility="collapsed")

        # Dolny przycisk wylogowania
        st.markdown(f'<div class="sidebar-footer-login">SQM DISPATCH<br>Zalogowano jako: {uzytkownik}</div>', unsafe_allow_html=True)
        
        # Stylizacja samego przycisku Wyloguj
        st.markdown(
            """
            <style>
            .stButton>button[key="logout_sidebar"] {
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: calc(100% - 40px);
                max-width: 250px;
                background-color: #8e44ad !important;
                color: white !important;
                border-radius: 12px !important;
                border: none;
                font-size: 0.9rem;
                padding: 10px;
            }
            </style>
            """, unsafe_allow_html=True
        )
        if st.button("Wyloguj się", key="logout_sidebar"):
            st.session_state["zalogowany"] = None
            st.rerun()

    # --- ROUTING (Przełączanie zakładek z plików ui_lukasz i ui_dawid) ---
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
        if wybor == "📱 Moje Zlecenia":
            ui_dawid.pokaz_panel()
