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
import ui_uzytkownicy # <--- NASZ NOWY MODUŁ ZARZĄDZANIA
import database
import style 

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(layout="wide", page_title="SQM DISPATCH", page_icon="📦")

# --- 2. OBSŁUGA CIASTECZEK ---
cookie_manager = stx.CookieManager(key="sqm_dispatch_v50_users")

# --- 3. INICJALIZACJA SESJI ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None
if "rola" not in st.session_state:
    st.session_state["rola"] = None
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
    return "Admin" # Fallback awaryjny

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

# --- 7. DYNAMICZNY EKRAN LOGOWANIA ---
if st.session_state["zalogowany"] is None:
    st.markdown('<div class="dashboard-header"><span style="font-size:2rem;">🔐</span><span class="dashboard-title" style="margin-left:10px;">SQM DISPATCH</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Zaloguj się do systemu:</div>', unsafe_allow_html=True)
    
    # Pobieramy na żywo listę użytkowników z arkusza "Uzytkownicy"
    lista_uz = database.pobierz_uzytkownikow()
    
    # TRYB AWARYJNY: Jeśli arkusz jest pusty lub źle wpięty, pozwólmy zalogować się Łukaszowi by to naprawić
    if not lista_uz:
        st.warning("⚠️ Baza użytkowników jest pusta! Uruchamiam tryb awaryjny (Login: Łukasz, PIN: 1234)")
        lista_uz = [{"Login": "Łukasz", "PIN": "1234", "Rola": "Admin"}]
        
    nazwy_uz = [str(u["Login"]) for u in lista_uz]
    
    col_log, _ = st.columns([1, 2])
    with col_log:
        wybrane_konto = st.selectbox("Wybierz swoje konto:", ["-- Wybierz --"] + nazwy_uz)
        
        if wybrane_konto != "-- Wybierz --":
            pin = st.text_input("Podaj kod PIN", type="password")
            if st.button("Zaloguj", type="primary", use_container_width=True):
                # Szukamy przypisanego do loginu PINu i Roli w pobranej liście
                dane_konta = next((u for u in lista_uz if str(u["Login"]) == wybrane_konto), None)
                
                if dane_konta and str(dane_konta["PIN"]) == pin:
                    st.session_state["zalogowany"] = wybrane_konto
                    st.session_state["rola"] = str(dane_konta["Rola"])
                    st.session_state["blokada_autologowania"] = False
                    
                    ts_log = str(int(time.time() * 1000))
                    cookie_manager.set("zalogowany", wybrane_konto, expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key=f"set_log_{ts_log}")
                    
                    wczytaj_ustawienia(wybrane_konto)
                    st.session_state["ustawienia_wczytane"] = True
                    st.rerun()
                else:
                    st.error("Błędny kod PIN!")

# --- 8. PANEL GŁÓWNY PO ZALOGOWANIU ---
else:
    uzytkownik = st.session_state["zalogowany"]
    rola = st.session_state.get("rola", "Admin")
    
    with st.sidebar:
        st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Zalogowano: <b>{uzytkownik}</b> <br><span style="font-size: 0.8rem; color: #94a3b8;">Rola: {rola}</span></div>', unsafe_allow_html=True)
        
        # --- DYNAMICZNE MENU NA PODSTAWIE ROLI ---
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
