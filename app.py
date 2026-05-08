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
import style  # <--- NASZ NOWY MODUŁ

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(layout="wide", page_title="SQM DISPATCH Dashboard", page_icon="📦")

# --- 2. OBSŁUGA CIASTECZEK (Pamięć 30 dni) ---
cookie_manager = stx.CookieManager(key="sqm_dispatch_ultra_pro_v28")

# --- 3. INICJALIZACJA SESJI I ZABEZPIECZEŃ ---
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

if "wybrane_konto" not in st.session_state:
    st.session_state["wybrane_konto"] = None

if "blokada_autologowania" not in st.session_state:
    st.session_state["blokada_autologowania"] = False

if "blokada_zapisu" not in st.session_state:
    st.session_state["blokada_zapisu"] = False

# --- 4. LOGIKA LOGOWANIA Z CIASTECZKA ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")

if zalogowany_cookie and st.session_state["zalogowany"] is None and not st.session_state["blokada_autologowania"]:
    st.session_state["blokada_zapisu"] = True
    st.session_state["zalogowany"] = zalogowany_cookie
    
    op, bl = database.pobierz_ustawienia_uzytkownika(zalogowany_cookie)
    st.session_state.bg_opacity = max(0.0, min(1.0, float(op)))
    st.session_state.bg_blur = max(0, min(20, int(bl)))
    
    st.session_state["blokada_zapisu"] = False

# Domyślne wartości UI
if "bg_opacity" not in st.session_state:
    st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state:
    st.session_state.bg_blur = 4

def zapisz_zmiany_ui():
    """Zapisuje ustawienia do bazy"""
    if st.session_state["zalogowany"] and not st.session_state["blokada_zapisu"]:
        database.zapisz_ustawienia_uzytkownika(st.session_state["zalogowany"], st.session_state.bg_opacity, st.session_state.bg_blur)

# --- 5. APLIKACJA STYLÓW Z ZEWNĘTRZNEGO MODUŁU ---
style.zastosuj_style(st.session_state.bg_opacity, st.session_state.bg_blur)

# --- 6. EKRAN LOGOWANIA (Z 3 DUŻYMI PRZYCISKAMI) ---
if st.session_state["zalogowany"] is None:
    st.markdown('<div class="dashboard-header"><span style="font-size:2rem;">🔐</span><span class="dashboard-title" style="margin-left:10px;">SQM DISPATCH</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Wybierz konto, aby wejść do systemu:</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👨‍💼\n\nŁukasz", use_container_width=True, key="login_l"): st.session_state["wybrane_konto"] = "Łukasz"
    with c2:
        if st.button("🚛\n\nDawid", use_container_width=True, key="login_d"): st.session_state["wybrane_konto"] = "Dawid"
    with c3:
        if st.button("🏭\n\nMagazyn", use_container_width=True, key="login_m"): st.session_state["wybrane_konto"] = "Magazyn"
    
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
                    st.error("Błąd konfiguracji haseł. Sprawdź plik secrets.")
                    st.stop()
                    
                if pin == poprawne_haslo:
                    st.session_state["blokada_zapisu"] = True
                    st.session_state["zalogowany"] = st.session_state["wybrane_konto"]
                    st.session_state["blokada_autologowania"] = False
                    
                    cookie_manager.set("zalogowany", st.session_state["zalogowany"], expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                    
                    op, bl = database.pobierz_ustawienia_uzytkownika(st.session_state["zalogowany"])
                    st.session_state.bg_opacity = max(0.0, min(1.0, float(op)))
                    st.session_state.bg_blur = max(0, min(20, int(bl)))
                    
                    st.session_state["blokada_zapisu"] = False
                    st.rerun()
                else:
                    st.error("Błędny kod PIN!")

# --- 7. PANEL GŁÓWNY PO ZALOGOWANIU ---
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

        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)

        if uzytkownik == "Łukasz":
            with st.expander("🛠️ Ustawienia UI"):
                st.slider("Krycie", 0.0, 1.0, step=0.05, key="bg_opacity", on_change=zapisz_zmiany_ui)
                st.slider("Rozmycie", 0, 20, step=1, key="bg_blur", on_change=zapisz_zmiany_ui)

        if st.button("Wyloguj się", use_container_width=True):
            st.session_state["blokada_zapisu"] = True
            try:
                cookie_manager.delete("zalogowany")
            except Exception:
                pass
            st.session_state["zalogowany"] = None
            st.session_state["wybrane_konto"] = None
            st.session_state["blokada_autologowania"] = True
            st.rerun()

    # --- 8. PEŁNY ROUTING ---
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
