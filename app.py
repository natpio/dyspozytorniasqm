import streamlit as st
import extra_streamlit_components as stx
from streamlit_autorefresh import st_autorefresh
import datetime
import ui_lukasz
import ui_dawid
import ui_magazyn
import ui_mapa
import ui_kalendarz
import database
import base64

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(layout="wide", page_title="SQM DISPATCH Dashboard", page_icon="📦")

# --- 2. OBSŁUGA CIASTECZEK ---
cookie_manager = stx.CookieManager(key="sqm_dispatch_v21")

# --- 3. INICJALIZACJA SESJI ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

if "wybrane_konto" not in st.session_state:
    st.session_state["wybrane_konto"] = None

if "blokada_autologowania" not in st.session_state:
    st.session_state["blokada_autologowania"] = False

if "blokada_zapisu" not in st.session_state:
    st.session_state["blokada_zapisu"] = False

# --- 4. LOGIKA LOGOWANIA ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")

if zalogowany_cookie and st.session_state["zalogowany"] is None and not st.session_state["blokada_autologowania"]:
    st.session_state["blokada_zapisu"] = True 
    st.session_state["zalogowany"] = zalogowany_cookie
    
    op, bl = database.pobierz_ustawienia_uzytkownika(zalogowany_cookie)
    st.session_state.bg_opacity = max(0.0, min(1.0, float(op)))
    st.session_state.bg_blur = max(0, min(20, int(bl)))
    st.session_state["blokada_zapisu"] = False

if "bg_opacity" not in st.session_state:
    st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state:
    st.session_state.bg_blur = 4

def zapisz_zmiany_ui():
    if st.session_state["zalogowany"] and not st.session_state["blokada_zapisu"]:
        database.zapisz_ustawienia_uzytkownika(st.session_state["zalogowany"], st.session_state.bg_opacity, st.session_state.bg_blur)

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

# --- 6. AGRESYWNY KOD CSS PREMIUM ---
local_css_string = """
[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { visibility: hidden !important; }
.stDeployButton { display: none !important; }

.stApp {
    background-image: url("BACKGROUND_URL_PLACEHOLDER") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}
.stApp::before {
    content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background-color: rgba(247, 249, 252, OPACITY_PLACEHOLDER) !important; 
    backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important; 
    -webkit-backdrop-filter: blur(BLUR_PLACEHOLDERpx) !important;
    z-index: 0 !important; pointer-events: none !important; 
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px) !important;
    background-size: 18px 18px !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * { color: #f8fafc !important; }

.sidebar-header { 
    background: -webkit-linear-gradient(45deg, #60a5fa, #f8fafc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 1.6rem !important; font-weight: 900 !important; padding: 1.5rem 1rem 0.5rem 1rem !important;
}
.sidebar-subheader { font-size: 0.85rem !important; color: #94a3b8 !important; padding: 0 1rem 1rem 1rem !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; }

[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none !important; }

div[role="radiogroup"] > label {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important; padding: 14px 18px !important; margin: 6px 1rem !important;
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}
div[role="radiogroup"] > label:hover { background: rgba(255, 255, 255, 0.08) !important; transform: translateX(8px) !important; }
div[role="radiogroup"] > label[data-checked="true"] { 
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.05)) !important;
    border-left: 4px solid #3b82f6 !important; transform: translateX(8px) !important;
}
div[role="radiogroup"] > label p { font-size: 1rem !important; font-weight: 500 !important; margin-left: 5px !important; }

[data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color: rgba(15, 23, 42, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 12px !important; margin: 1rem !important;
}

div[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
    color: white !important; font-weight: 800 !important; border-radius: 12px !important; border: none !important;
    width: 100% !important; padding: 12px !important; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2) !important; margin-top: 1rem;
}

.card-container { 
    background: white !important; border-radius: 15px !important; box-shadow: 0 8px 25px rgba(0,0,0,0.05) !important; 
    padding: 20px !important; margin-bottom: 15px !important; border: 1px solid #e2e8f0 !important; 
}
.card-value { font-size: 2.4rem !important; font-weight: bold !important; color: #0f172a !important; }

@media (prefers-color-scheme: dark) {
    .stApp::before { background-color: rgba(15, 23, 42, OPACITY_PLACEHOLDER) !important; }
    .card-container {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
        border: 1px solid #334155 !important;
    }
    .card-value, .dashboard-title { color: #f8fafc !important; }
}
"""

local_css_string = local_css_string.replace("BACKGROUND_URL_PLACEHOLDER", bg_img_url)
local_css_string = local_css_string.replace("OPACITY_PLACEHOLDER", str(st.session_state.bg_opacity))
local_css_string = local_css_string.replace("BLUR_PLACEHOLDER", str(st.session_state.bg_blur))
st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)

# --- 7. EKRAN LOGOWANIA ---
if st.session_state["zalogowany"] is None:
    st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
    st.write("Wybierz konto, aby uzyskać dostęp do systemu:")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👨‍💼 Łukasz", use_container_width=True, key="login_l"): st.session_state["wybrane_konto"] = "Łukasz"
    with c2:
        if st.button("🚛 Dawid", use_container_width=True, key="login_d"): st.session_state["wybrane_konto"] = "Dawid"
    with c3:
        if st.button("🏭 Magazyn", use_container_width=True, key="login_m"): st.session_state["wybrane_konto"] = "Magazyn"
    
    if st.session_state["wybrane_konto"]:
        st.info(f"Konto: **{st.session_state['wybrane_konto']}**")
        pin = st.text_input("Podaj kod PIN", type="password")
        if st.button("Zaloguj", type="primary", use_container_width=True):
            key = st.session_state["wybrane_konto"].lower().replace("ł", "l")
            if pin == str(st.secrets["passwords"][key]):
                st.session_state["blokada_zapisu"] = True
                st.session_state["zalogowany"] = st.session_state["wybrane_konto"]
                st.session_state["blokada_autologowania"] = False
                
                waznosc = datetime.datetime.now() + datetime.timedelta(days=30)
                cookie_manager.set("zalogowany", st.session_state["zalogowany"], expires_at=waznosc)
                
                op, bl = database.pobierz_ustawienia_uzytkownika(st.session_state["zalogowany"])
                st.session_state.bg_opacity = max(0.0, min(1.0, float(op)))
                st.session_state.bg_blur = max(0, min(20, int(bl)))
                
                st.session_state["blokada_zapisu"] = False
                st.rerun()
            else:
                st.error("Nieprawidłowy PIN!")

# --- 8. PANEL GŁÓWNY PO ZALOGOWANIU ---
else:
    uzytkownik = st.session_state["zalogowany"]
    with st.sidebar:
        st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.write(f"Zalogowano jako: **{uzytkownik}**")
        
        if uzytkownik == "Łukasz":
            wybor = st.radio("M", ["⚙️ Dashboard", "➕ Nowy Wpis", "📍 Mapa Routing", "🗓️ Kalendarz", "🏭 Logistyka", "🛠️ Konsola Admin.", "📂 Archiwum"], label_visibility="collapsed")
        elif uzytkownik == "Dawid":
            wybor = st.radio("M", ["📱 Moje Zlecenia"], label_visibility="collapsed")
        else:
            wybor = st.radio("M", ["🏭 Tablica Magazynowa"], label_visibility="collapsed")

        if uzytkownik == "Łukasz":
            with st.expander("🛠️ Ustawienia UI"):
                st.slider("Krycie", 0.0, 1.0, step=0.05, key="bg_opacity", on_change=zapisz_zmiany_ui)
                st.slider("Rozmycie", 0, 20, step=1, key="bg_blur", on_change=zapisz_zmiany_ui)

        if st.button("Wyloguj się"):
            st.session_state["blokada_zapisu"] = True
            try:
                cookie_manager.delete("zalogowany")
            except:
                pass
            st.session_state["zalogowany"] = None
            st.session_state["wybrane_konto"] = None
            st.session_state["blokada_autologowania"] = True
            st.rerun()

    # --- 9. ROUTING ---
    if uzytkownik == "Łukasz":
        st_autorefresh(interval=60000, key="refresh_l")
        if wybor == "⚙️ Dashboard": ui_lukasz.pokaz_dashboard()
        elif wybor == "➕ Nowy Wpis": ui_lukasz.pokaz_formularz()
        elif wybor == "📍 Mapa Routing": ui_mapa.pokaz_mape()
        elif wybor == "🗓️ Kalendarz": ui_kalendarz.pokaz_kalendarz()
        elif wybor == "🏭 Logistyka": ui_lukasz.pokaz_magazyn()
        elif wybor == "🛠️ Konsola Admin.": ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📂 Archiwum": ui_lukasz.pokaz_archiwum()
    elif uzytkownik == "Dawid":
        ui_dawid.pokaz_panel()
    else:
        st_autorefresh(interval=30000, key="refresh_m")
        ui_magazyn.pokaz_tablice()
