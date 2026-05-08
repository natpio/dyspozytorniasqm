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
import style 

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(layout="wide", page_title="SQM DISPATCH", page_icon="📦")

# --- 2. OBSŁUGA CIASTECZEK ---
cookie_manager = stx.CookieManager(key="sqm_dispatch_v39_iron")

# --- 3. INICJALIZACJA SESJI ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None
if "wybrane_konto" not in st.session_state:
    st.session_state["wybrane_konto"] = None
if "blokada_autologowania" not in st.session_state:
    st.session_state["blokada_autologowania"] = False
if "ustawienia_wczytane" not in st.session_state:
    st.session_state["ustawienia_wczytane"] = False

# --- 4. ZAAWANSOWANA FUNKCJA WCZYTYWANIA (ODPORNA NA F5 I CACHE) ---
def wczytaj_ustawienia(uzytkownik):
    # 1. Próba z Ciasteczka (Omija całkowicie opóźnienia Google Sheets i F5)
    cookie_op = cookie_manager.get(f"ui_op_{uzytkownik}")
    cookie_bl = cookie_manager.get(f"ui_bl_{uzytkownik}")
    
    if cookie_op is not None and cookie_bl is not None:
        try:
            st.session_state["bg_opacity"] = max(0.0, min(1.0, float(cookie_op)))
            st.session_state["bg_blur"] = max(0, min(20, int(float(cookie_bl))))
            return # Jeśli mamy ciasteczko, kończymy - to najświeższe dane!
        except: pass
        
    # 2. Próba z bazy danych Google Sheets (Fallback)
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
        # 3. Twardy Reset Bezpieczeństwa
        st.session_state["bg_opacity"] = 0.75
        st.session_state["bg_blur"] = 4

# --- 5. LOGIKA ŁADOWANIA DANYCH ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")

if zalogowany_cookie and not st.session_state["ustawienia_wczytane"] and not st.session_state["blokada_autologowania"]:
    st.session_state["zalogowany"] = zalogowany_cookie
    wczytaj_ustawienia(zalogowany_cookie)
    st.session_state["ustawienia_wczytane"] = True
    st.rerun()

# Domyślne wartości
if "bg_opacity" not in st.session_state:
    st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state:
    st.session_state.bg_blur = 4

# --- 6. APLIKACJA STYLÓW Z MODUŁU style.py ---
style.zastosuj_style(st.session_state.bg_opacity, st.session_state.bg_blur)

# --- 7. EKRAN LOGOWANIA ---
if st.session_state["zalogowany"] is None:
    st.markdown('<div class="dashboard-header"><span style="font-size:2rem;">🔐</span><span class="dashboard-title" style="margin-left:10px;">SQM DISPATCH</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Wybierz konto:</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👨‍💼\n\nŁukasz", use_container_width=True): st.session_state["wybrane_konto"] = "Łukasz"
    with c2:
        if st.button("🚛\n\nDawid", use_container_width=True): st.session_state["wybrane_konto"] = "Dawid"
    with c3:
        if st.button("🏭\n\nMagazyn", use_container_width=True): st.session_state["wybrane_konto"] = "Magazyn"
    
    if st.session_state["wybrane_konto"]:
        st.markdown(f"<br><div style='padding: 15px; border-radius: 10px; background-color: rgba(59, 130, 246, 0.1); border-left: 5px solid #3b82f6;'>Logowanie do konta: <b>{st.session_state['wybrane_konto']}</b></div><br>", unsafe_allow_html=True)
        col_pin, _ = st.columns([1, 2])
        with col_pin:
            pin = st.text_input("Podaj kod PIN", type="password")
            if st.button("Zaloguj", type="primary", use_container_width=True):
                key = st.session_state["wybrane_konto"].lower().replace("ł", "l")
                try:
                    poprawne_haslo = str(st.secrets["passwords"][key])
                except KeyError:
                    st.error("Błąd pliku secrets.")
                    st.stop()
                    
                if pin == poprawne_haslo:
                    st.session_state["zalogowany"] = st.session_state["wybrane_konto"]
                    st.session_state["blokada_autologowania"] = False
                    
                    cookie_manager.set("zalogowany", st.session_state["zalogowany"], expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                    
                    wczytaj_ustawienia(st.session_state["zalogowany"])
                    st.session_state["ustawienia_wczytane"] = True
                    st.rerun()
                else:
                    st.error("Błędny kod PIN!")

# --- 8. PANEL GŁÓWNY PO ZALOGOWANIU ---
else:
    uzytkownik = st.session_state["zalogowany"]
    with st.sidebar:
        st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-subheader">Zalogowano: <b>{uzytkownik}</b></div>', unsafe_allow_html=True)
        
        if uzytkownik == "Łukasz":
            wybor = st.radio("M", [
                "⚙️ Dashboard", "➕ Nowy Wpis", "📍 Mapa Routing", 
                "🗓️ Kalendarz", "🏭 Logistyka", "🛠️ Konsola Admin.", "📂 Archiwum"
            ], label_visibility="collapsed")
        elif uzytkownik == "Dawid":
            wybor = st.radio("M", ["📱 Moje Zlecenia"], label_visibility="collapsed")
        else:
            wybor = st.radio("M", ["🏭 Tablica Magazynowa"], label_visibility="collapsed")

        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)

        if uzytkownik == "Łukasz":
            with st.expander("🛠️ Ustawienia UI"):
                st.slider("Krycie", 0.0, 1.0, step=0.05, key="bg_opacity")
                st.slider("Rozmycie", 0, 20, step=1, key="bg_blur")
                
                if st.button("💾 Zapisz jako domyślne", use_container_width=True):
                    # 1. Wysyłamy do Google Sheets (Dla innych urządzeń)
                    try: database.zapisz_ustawienia_uzytkownika(uzytkownik, st.session_state.bg_opacity, st.session_state.bg_blur)
                    except: pass
                    
                    # 2. Zapisujemy TWARDO do ciasteczka! (Dzięki temu F5 nas nie pokona)
                    waznosc = datetime.datetime.now() + datetime.timedelta(days=30)
                    cookie_manager.set(f"ui_op_{uzytkownik}", st.session_state.bg_opacity, expires_at=waznosc)
                    cookie_manager.set(f"ui_bl_{uzytkownik}", st.session_state.bg_blur, expires_at=waznosc)
                    
                    # 3. Zmuszamy chmurę do wyczyszczenia pamięci
                    try: st.cache_data.clear()
                    except: pass
                    try: st.cache_resource.clear()
                    except: pass
                    
                    st.toast("Zapisano! Ustawienia zabezpieczone lokalnie i w chmurze.", icon="✅")

        if st.button("Wyloguj się", use_container_width=True):
            try: cookie_manager.delete("zalogowany")
            except Exception: pass
            st.session_state["zalogowany"] = None
            st.session_state["wybrane_konto"] = None
            st.session_state["ustawienia_wczytane"] = False
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
        _, col_main, _ = st.columns([1, 2, 1])
        with col_main:
            ui_dawid.pokaz_panel()
    else:
        st_autorefresh(interval=30000, key="refresh_m")
        ui_magazyn.pokaz_tablice()
