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

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(layout="wide", page_title="SQM DISPATCH", page_icon="📦")

# --- 2. OBSŁUGA CIASTECZEK ---
cookie_manager = stx.CookieManager(key="sqm_dispatch_v55_premium")

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
    """Pobiera rolę użytkownika na podstawie ciasteczka"""
    uzytkownicy = database.pobierz_uzytkownikow()
    for u in uzytkownicy:
        if str(u.get("Login", "")) == login:
            return str(u.get("Rola", ""))
    return "Admin"

# --- 4. ZAAWANSOWANA FUNKCJA WCZYTYWANIA UI ---
def wczytaj_ustawienia(uzytkownik):
    cookie_op = cookie_manager.get(f"ui_op_{uzytkownik}")
    cookie_bl = cookie_manager.get(f"ui_bl_{uzytkownik}")
    
    if cookie_op is not None and cookie_bl is not None:
        try:
            st.session_state["bg_opacity"] = max(0.0, min(1.0, float(cookie_op)))
            st.session_state["bg_blur"] = max(0, min(20, int(float(cookie_bl))))
            return
        except: pass
        
    try:
        wynik = database.pobierz_ustawienia_uzytkownika(uzytkownik)
        if isinstance(wynik, tuple) and len(wynik) >= 2:
            op, bl = wynik[0], wynik[1]
        else:
            op, bl = 0.75, 4
            
        op_str = str(op).replace(',', '.').strip()
        bl_str = str(bl).replace(',', '.').strip()
        
        if not op_str or op_str.lower() == 'none': op_str = "0.75"
        if not bl_str or bl_str.lower() == 'none': bl_str = "4"
        
        st.session_state["bg_opacity"] = max(0.0, min(1.0, float(op_str)))
        st.session_state["bg_blur"] = max(0, min(20, int(float(bl_str))))
    except Exception:
        st.session_state["bg_opacity"] = 0.75
        st.session_state["bg_blur"] = 4

# --- 5. LOGIKA ŁADOWANIA DANYCH Z CIASTECZKA ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")

if zalogowany_cookie and not st.session_state["ustawienia_wczytane"] and not st.session_state["blokada_autologowania"]:
    st.session_state["zalogowany"] = zalogowany_cookie
    st.session_state["rola"] = pobierz_role_z_bazy(zalogowany_cookie)
    wczytaj_ustawienia(zalogowany_cookie)
    st.session_state["ustawienia_wczytane"] = True
    st.rerun()

if "bg_opacity" not in st.session_state:
    st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state:
    st.session_state.bg_blur = 4

# --- 6. APLIKACJA STYLÓW ---
style.zastosuj_style(st.session_state.bg_opacity, st.session_state.bg_blur)

# --- 7. PREMIUM EKRAN LOGOWANIA ---
if st.session_state["zalogowany"] is None:
    
    # CSS definiujący nowoczesny wygląd karty logowania (Glassmorphism)
    st.markdown("""
    <style>
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 8vh;
    }
    .login-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px 50px;
        width: 100%;
        max-width: 650px;
        text-align: center;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    .login-title {
        font-size: 2.5rem;
        font-weight: 900;
        color: #f8fafc;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    .login-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 35px;
    }
    /* Stylizacja przycisków wyboru konta */
    div[data-testid="stButton"] > button {
        border-radius: 16px !important;
        height: auto !important;
        padding: 15px 10px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        background-color: rgba(255,255,255,0.03) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #3b82f6 !important;
        background-color: rgba(59, 130, 246, 0.1) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.3) !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    lista_uz = database.pobierz_uzytkownikow()
    
    if not lista_uz:
        st.warning("⚠️ Baza użytkowników jest pusta! Uruchamiam tryb awaryjny (Login: Łukasz, PIN: 1234)")
        lista_uz = [{"Login": "Łukasz", "PIN": "1234", "Rola": "Admin"}]

    _, col_center, _ = st.columns([1, 2, 1])

    with col_center:
        st.markdown('<div class="login-wrapper"><div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🔐 SQM DISPATCH</div>', unsafe_allow_html=True)
        
        # WIDOK 1: WYBÓR KONTA (Kafelki)
        if st.session_state["wybrane_konto"] is None:
            st.markdown('<div class="login-subtitle">Wybierz swój profil, aby wejść do systemu</div>', unsafe_allow_html=True)
            
            # Układamy przyciski w siatkę (3 w rzędzie)
            cols = st.columns(3)
            for i, uz in enumerate(lista_uz):
                login = str(uz["Login"])
                rola = str(uz.get("Rola", ""))
                
                # Dynamiczna ikona bazująca na roli z Google Sheets
                if rola == "Admin": icon = "👨‍💼"
                elif rola == "Kierowca": icon = "🚚"
                elif rola == "Magazyn": icon = "🏭"
                else: icon = "👤"
                
                with cols[i % 3]:
                    # Używamy natywnych przycisków, ale stylizowanych przez nasz CSS wyżej
                    if st.button(f"{icon}\n\n{login}", key=f"btn_{login}", use_container_width=True):
                        st.session_state["wybrane_konto"] = login
                        st.rerun()
                        
        # WIDOK 2: WPISYWANIE PINU
        else:
            wybrane_konto = st.session_state["wybrane_konto"]
            dane_konta = next((u for u in lista_uz if str(u["Login"]) == wybrane_konto), None)
            rola = str(dane_konta.get("Rola", "")) if dane_konta else ""
            icon = "👨‍💼" if rola == "Admin" else "🚚" if rola == "Kierowca" else "🏭" if rola == "Magazyn" else "👤"

            st.markdown(f'<div class="login-subtitle" style="color: #3b82f6; font-weight: bold;">{icon} Zaloguj jako: {wybrane_konto}</div>', unsafe_allow_html=True)
            
            pin = st.text_input("Wprowadź kod PIN", type="password", placeholder="****")
            
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
                        st.session_state["rola"] = rola
                        st.session_state["blokada_autologowania"] = False
                        
                        ts_log = str(int(time.time() * 1000))
                        cookie_manager.set("zalogowany", wybrane_konto, expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key=f"set_log_{ts_log}")
                        
                        wczytaj_ustawienia(wybrane_konto)
                        st.session_state["ustawienia_wczytane"] = True
                        st.rerun()
                    else:
                        st.error("Błędny kod PIN!")
                        
        st.markdown('</div></div>', unsafe_allow_html=True) # Zamykamy tagi CSS


# --- 8. PANEL GŁÓWNY PO ZALOGOWANIU ---
else:
    uzytkownik = st.session_state["zalogowany"]
    rola = st.session_state.get("rola", "Admin")
    
    with st.sidebar:
        st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Zalogowano: <b>{uzytkownik}</b> <br><span style="font-size: 0.8rem; color: #94a3b8;">Rola: {rola}</span></div>', unsafe_allow_html=True)
        
        if rola == "Admin":
            wybor = st.radio("M", [
                "⚙️ Dashboard", "➕ Nowy Wpis", "📍 Mapa Routing", 
                "🗓️ Kalendarz", "🏭 Logistyka", "🛠️ Konsola Admin.", "📂 Archiwum", "👥 Użytkownicy"
            ], label_visibility="collapsed")
        elif rola == "Kierowca":
            wybor = st.radio("M", ["📱 Moje Zlecenia"], label_visibility="collapsed")
        else: # Magazyn 
            wybor = st.radio("M", ["🏭 Tablica Magazynowa"], label_visibility="collapsed")

        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)

        if rola == "Admin":
            with st.expander("🛠️ Ustawienia UI"):
                st.slider("Krycie", 0.0, 1.0, step=0.05, key="bg_opacity")
                st.slider("Rozmycie", 0, 20, step=1, key="bg_blur")
                
                if st.button("💾 Zapisz jako domyślne", use_container_width=True):
                    try: database.zapisz_ustawienia_uzytkownika(uzytkownik, st.session_state.bg_opacity, st.session_state.bg_blur)
                    except: pass
                    
                    ts_op = str(int(time.time() * 1000)) + "_op"
                    ts_bl = str(int(time.time() * 1000)) + "_bl"
                    waznosc = datetime.datetime.now() + datetime.timedelta(days=30)
                    
                    cookie_manager.set(f"ui_op_{uzytkownik}", str(st.session_state.bg_opacity), expires_at=waznosc, key=f"set_{ts_op}")
                    cookie_manager.set(f"ui_bl_{uzytkownik}", str(st.session_state.bg_blur), expires_at=waznosc, key=f"set_{ts_bl}")
                    
                    st.cache_data.clear()
                    st.toast("Zapisano! Ustawienia zabezpieczone przed resetem F5.", icon="✅")

        if st.button("Wyloguj się", use_container_width=True):
            ts_del = str(int(time.time() * 1000))
            try: cookie_manager.delete("zalogowany", key=f"del_log_{ts_del}")
            except Exception: pass
            st.session_state["zalogowany"] = None
            st.session_state["rola"] = None
            st.session_state["wybrane_konto"] = None
            st.session_state["ustawienia_wczytane"] = False
            st.session_state["blokada_autologowania"] = True
            st.rerun()

    # --- 9. ROUTING DO MODUŁÓW UI ---
    if rola == "Admin":
        st_autorefresh(interval=60000, key="refresh_admin")
        if wybor == "⚙️ Dashboard": ui_lukasz.pokaz_dashboard()
        elif wybor == "➕ Nowy Wpis": ui_lukasz.pokaz_formularz()
        elif wybor == "📍 Mapa Routing": ui_mapa.pokaz_mape()
        elif wybor == "🗓️ Kalendarz": ui_kalendarz.pokaz_kalendarz()
        elif wybor == "🏭 Logistyka": ui_lukasz.pokaz_magazyn()
        elif wybor == "🛠️ Konsola Admin.": ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📂 Archiwum": ui_lukasz.pokaz_archiwum()
        elif wybor == "👥 Użytkownicy": ui_uzytkownicy.pokaz_panel_uzytkownikow()
    
    elif rola == "Kierowca":
        _, col_main, _ = st.columns([1, 2, 1])
        with col_main:
            ui_dawid.pokaz_panel() 
    
    else: # Magazyn
        st_autorefresh(interval=30000, key="refresh_magazyn")
        ui_magazyn.pokaz_tablice()
