import streamlit as st
import extra_streamlit_components as stx
from streamlit_autorefresh import st_autorefresh
import datetime
import time
import ui_lukasz
import ui_dawid
import ui_magazyn
import ui_mapa      
import ui_kalendarz 
import ui_uzytkownicy
import database
import style 
import config

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(layout="wide", page_title="SQM DISPATCH", page_icon="📦")

# --- 2. OBSŁUGA CIASTECZEK (Persystencja sesji) ---
cookie_manager = stx.CookieManager(key="sqm_dispatch_v61_perfect_ui")

# --- 3. INICJALIZACJA SESJI ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None
if "rola" not in st.session_state:
    st.session_state["rola"] = None
if "wybrane_konto" not in st.session_state:
    st.session_state["wybrane_konto"] = None
if "blokada_autologowania" not in st.session_state:
    st.session_state["blokada_autologowania"] = False
if "ustawienia_wczytane" not in st.session_state:
    st.session_state["ustawienia_wczytane"] = False

# --- FUNKCJA POMOCNICZA: POBRANIE ROLI ---
def pobierz_role_z_bazy(login):
    """Pobiera rolę użytkownika z Google Sheets na podstawie loginu"""
    uzytkownicy = database.pobierz_uzytkownikow()
    for u in uzytkownicy:
        if str(u.get("Login", "")) == login:
            return str(u.get("Rola", ""))
    return "Admin"

# --- 4. FUNKCJA WCZYTYWANIA USTAWIEŃ UI ---
def wczytaj_ustawienia(uzytkownik):
    """Pobiera preferencje wizualne z ciasteczek lub Google Sheets"""
    cookie_op = cookie_manager.get(f"ui_op_{uzytkownik}")
    cookie_bl = cookie_manager.get(f"ui_bl_{uzytkownik}")
    
    if cookie_op is not None and cookie_bl is not None:
        try:
            st.session_state["bg_opacity"] = max(0.0, min(1.0, float(cookie_op)))
            st.session_state["bg_blur"] = max(0, min(20, int(float(cookie_bl))))
            return
        except: pass
        
    try:
        op, bl = database.pobierz_ustawienia_uzytkownika(uzytkownik)
        op_str = str(op).replace(',', '.').strip()
        bl_str = str(bl).replace(',', '.').strip()
        
        st.session_state["bg_opacity"] = max(0.0, min(1.0, float(op_str if op_str != 'None' else 0.75)))
        st.session_state["bg_blur"] = max(0, min(20, int(float(bl_str if bl_str != 'None' else 4))))
    except:
        st.session_state["bg_opacity"] = 0.75
        st.session_state["bg_blur"] = 4

# --- 5. LOGIKA AUTOLOGOWANIA ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")

if zalogowany_cookie and not st.session_state["ustawienia_wczytane"] and not st.session_state["blokada_autologowania"]:
    st.session_state["zalogowany"] = zalogowany_cookie
    st.session_state["rola"] = pobierz_role_z_bazy(zalogowany_cookie)
    wczytaj_ustawienia(zalogowany_cookie)
    st.session_state["ustawienia_wczytane"] = True
    st.rerun()

# Wartości domyślne przed załadowaniem profilu
if "bg_opacity" not in st.session_state:
    st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state:
    st.session_state.bg_blur = 4

# --- 6. APLIKACJA STYLÓW TŁA ---
style.zastosuj_style(st.session_state.bg_opacity, st.session_state.bg_blur)

# --- 7. FIX: NIEZNISZCZALNY EKRAN LOGOWANIA (Marker CSS) ---
if st.session_state["zalogowany"] is None:
    
    # CSS używający technologii :has() - formatuje TYLKO tę kolumnę, która ma w sobie znacznik .login-marker
    st.markdown("""
    <style>
    /* Prawdziwe celowanie w naszą kolumnę */
    div[data-testid="column"]:has(.login-marker) {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.98)) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 28px !important;
        padding: 40px !important;
        box-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.8) !important;
        margin-top: 5vh;
    }

    /* Wymuszamy czytelne białe teksty wewnątrz karty logowania */
    div[data-testid="column"]:has(.login-marker) p,
    div[data-testid="column"]:has(.login-marker) label,
    div[data-testid="column"]:has(.login-marker) h1 {
        color: #f8fafc !important;
        text-align: center !important;
    }

    /* Pigułki / Przyciski uzytkowników - Mocny kontrast */
    div[data-testid="column"]:has(.login-marker) div[data-testid="stButton"] > button {
        border-radius: 16px !important;
        padding: 15px 10px !important;
        height: auto !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        background-color: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    /* Efekt podświetlenia po najechaniu */
    div[data-testid="column"]:has(.login-marker) div[data-testid="stButton"] > button:hover {
        border-color: #3b82f6 !important;
        background-color: rgba(59, 130, 246, 0.3) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3) !important;
    }

    /* Przycisk akcji (Zaloguj) na kolorowo */
    div[data-testid="column"]:has(.login-marker) div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(90deg, #3b82f6, #2563eb) !important;
        border: none !important;
    }
    
    /* Ukrycie paska top Streamlita */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    lista_uz = database.pobierz_uzytkownikow()
    
    if not lista_uz:
        lista_uz = [{"Login": "Łukasz", "PIN": "1234", "Rola": "Admin"}]

    _, col_center, _ = st.columns([1, 1.2, 1])

    with col_center:
        # MAGICZNY ZNACZNIK - na jego podstawie działa nasz CSS
        st.markdown('<span class="login-marker"></span>', unsafe_allow_html=True)
        
        st.markdown('<h1 style="margin-bottom: 10px; letter-spacing: -1px;">🔐 SQM DISPATCH</h1>', unsafe_allow_html=True)
        
        # ETAP 1: WYBÓR PROFILU
        if st.session_state["wybrane_konto"] is None:
            st.markdown('<p style="margin-bottom: 30px; font-size:1.1rem;">Wybierz profil, aby kontynuować</p>', unsafe_allow_html=True)
            
            # Siatka 3 kolumn na przyciski osób
            cols = st.columns(3)
            for i, uz in enumerate(lista_uz):
                login = str(uz["Login"])
                rola = str(uz.get("Rola", ""))
                icon = "👨‍💼" if rola == "Admin" else "🚚" if rola == "Kierowca" else "🏭" if rola == "Magazyn" else "👤"
                
                with cols[i % 3]:
                    if st.button(f"{icon}\n\n{login}", key=f"login_{login}", use_container_width=True):
                        st.session_state["wybrane_konto"] = login
                        st.rerun()
                        
        # ETAP 2: WERYFIKACJA PIN
        else:
            wybrane_konto = st.session_state["wybrane_konto"]
            dane_konta = next((u for u in lista_uz if str(u["Login"]) == wybrane_konto), None)
            
            st.markdown(f'<p style="color: #60a5fa !important; font-weight: bold; font-size: 1.2rem; margin-bottom: 25px;">Zaloguj jako: {wybrane_konto}</p>', unsafe_allow_html=True)
            
            pin = st.text_input("Wprowadź swój PIN", type="password", placeholder="****")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔙 Zmień konto", use_container_width=True):
                    st.session_state["wybrane_konto"] = None
                    st.rerun()
            with c2:
                if st.button("Wejdź", type="primary", use_container_width=True):
                    if dane_konta and str(dane_konta["PIN"]) == pin:
                        st.session_state["zalogowany"] = wybrane_konto
                        st.session_state["rola"] = str(dane_konta.get("Rola", "Admin"))
                        
                        # Zapis ciasteczka logowania
                        ts = str(int(time.time() * 1000))
                        cookie_manager.set("zalogowany", wybrane_konto, expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key=f"set_log_{ts}")
                        
                        wczytaj_ustawienia(wybrane_konto)
                        st.session_state["ustawienia_wczytane"] = True
                        st.rerun()
                    else:
                        st.error("Błędny kod PIN!")

# --- 8. PANEL GŁÓWNY (PO LOGOWANIU) ---
else:
    uzytkownik = st.session_state["zalogowany"]
    rola = st.session_state.get("rola", "Admin")
    
    with st.sidebar:
        st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Użytkownik: <b>{uzytkownik}</b> <br><span style="font-size: 0.8rem; color: #94a3b8;">Dostęp: {rola}</span></div>', unsafe_allow_html=True)
        
        # Menu zależne od roli
        if rola == "Admin":
            wybor = st.radio("Nawigacja", [
                "⚙️ Dashboard", "➕ Nowy Wpis", "📍 Mapa Routing", 
                "🗓️ Kalendarz", "🏭 Logistyka", "🛠️ Konsola Admin.", "📂 Archiwum", "👥 Użytkownicy"
            ], label_visibility="collapsed")
        elif rola == "Kierowca":
            wybor = st.radio("Nawigacja", ["📱 Moje Zlecenia"], label_visibility="collapsed")
        else: # Magazyn
            wybor = st.radio("Nawigacja", ["🏭 Tablica Magazynowa"], label_visibility="collapsed")

        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)

        if rola == "Admin":
            with st.expander("🛠️ Personalizacja UI"):
                st.slider("Przezroczystość", 0.0, 1.0, step=0.05, key="bg_opacity")
                st.slider("Rozmycie tła", 0, 20, step=1, key="bg_blur")
                
                if st.button("💾 Zastosuj na stałe", use_container_width=True):
                    database.zapisz_ustawienia_uzytkownika(uzytkownik, st.session_state.bg_opacity, st.session_state.bg_blur)
                    
                    waznosc = datetime.datetime.now() + datetime.timedelta(days=30)
                    ts = str(int(time.time() * 1000))
                    cookie_manager.set(f"ui_op_{uzytkownik}", str(st.session_state.bg_opacity), expires_at=waznosc, key=f"s_op_{ts}")
                    cookie_manager.set(f"ui_bl_{uzytkownik}", str(st.session_state.bg_blur), expires_at=waznosc, key=f"s_bl_{ts}")
                    
                    st.toast("Zapisano ustawienia!")

        if st.button("Wyloguj się", use_container_width=True):
            ts = str(int(time.time() * 1000))
            try: cookie_manager.delete("zalogowany", key=f"del_log_{ts}")
            except: pass
            st.session_state.clear()
            st.rerun()

    # --- 9. ROUTING DO MODUŁÓW ---
    if rola == "Admin":
        st_autorefresh(interval=60000, key="auto_ref_admin")
        if wybor == "⚙️ Dashboard": ui_lukasz.pokaz_dashboard()
        elif wybor == "➕ Nowy Wpis": ui_lukasz.pokaz_formularz()
        elif wybor == "📍 Mapa Routing": ui_mapa.pokaz_mape()
        elif wybor == "🗓️ Kalendarz": ui_kalendarz.pokaz_kalendarz()
        elif wybor == "🏭 Logistyka": ui_lukasz.pokaz_magazyn()
        elif wybor == "🛠️ Konsola Admin.": ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📂 Archiwum": ui_lukasz.pokaz_archiwum()
        elif wybor == "👥 Użytkownicy": ui_uzytkownicy.pokaz_panel_uzytkownikow()
    
    elif rola == "Kierowca":
        _, col_mob, _ = st.columns([1, 2, 1])
        with col_mob:
            ui_dawid.pokaz_panel() 
    
    else: # Magazyn
        st_autorefresh(interval=30000, key="auto_ref_mag")
        ui_magazyn.pokaz_tablice()
