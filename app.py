import streamlit as st
import extra_streamlit_components as stx
from streamlit_autorefresh import st_autorefresh
import datetime
from zoneinfo import ZoneInfo
import time
import pandas as pd
import ui_lukasz
import ui_dawid
import ui_magazyn
import ui_mapa      
import ui_kalendarz 
import ui_uzytkownicy
import database
import style 
import data_processing

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(layout="wide", page_title="SQM CONTROL TOWER OS", page_icon="📍", initial_sidebar_state="collapsed")

cookie_manager = stx.CookieManager(key="sqm_control_tower_v90")

# Inicjalizacja kluczowych zmiennych systemowych
if "zalogowany" not in st.session_state: st.session_state["zalogowany"] = None
if "rola" not in st.session_state: st.session_state["rola"] = None
if "wybrane_konto" not in st.session_state: st.session_state["wybrane_konto"] = None
if "blokada_autologowania" not in st.session_state: st.session_state["blokada_autologowania"] = False
if "ustawienia_wczytane" not in st.session_state: st.session_state["ustawienia_wczytane"] = False
if "aktywny_modul" not in st.session_state: st.session_state["aktywny_modul"] = "Control Tower"

# Inicjalizacja twardych stanów interfejsu
if "bg_opacity" not in st.session_state: st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state: st.session_state.bg_blur = 4
if "suwak_opacity" not in st.session_state: st.session_state.suwak_opacity = 0.75
if "suwak_blur" not in st.session_state: st.session_state.suwak_blur = 4

def pobierz_role_z_bazy(login):
    uzytkownicy = database.pobierz_uzytkownikow()
    for u in uzytkownicy:
        if str(u.get("Login", "")) == login:
            return str(u.get("Rola", ""))
    return "Admin"

def wczytaj_ustawienia_z_bazy(uzytkownik):
    """Pobiera parametry z Google Sheets i twardo nadpisuje duchy w przeglądarce."""
    op, bl = database.pobierz_ustawienia_uzytkownika(uzytkownik)
    st.session_state["bg_opacity"] = float(op)
    st.session_state["bg_blur"] = int(bl)
    st.session_state["suwak_opacity"] = float(op)
    st.session_state["suwak_blur"] = int(bl)

# --- AUTOLOGOWANIE ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")
if zalogowany_cookie and st.session_state["zalogowany"] is None and not st.session_state["blokada_autologowania"]:
    st.session_state["zalogowany"] = zalogowany_cookie
    st.session_state["rola"] = pobierz_role_z_bazy(zalogowany_cookie)
    wczytaj_ustawienia_z_bazy(zalogowany_cookie)
    st.session_state["ustawienia_wczytane"] = True
    st.rerun()

# Aplikowanie stylów NA SAMYM POCZĄTKU na podstawie zmiennych
style.zastosuj_style(st.session_state.bg_opacity, st.session_state.bg_blur)

# ==========================================
# 🔐 WARSTWA UWIERZYTELNIANIA (LOGOWANIE)
# ==========================================
if st.session_state["zalogowany"] is None:
    lista_uz = database.pobierz_uzytkownikow()
    if not lista_uz:
        lista_uz = [{"Login": "Piotr", "PIN": "1234", "Rola": "Admin"}]

    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1 style="margin-bottom: 10px; text-align:center; letter-spacing: -1px; color:#f8fafc;">🔐 SQM SYSTEM OS</h1>', unsafe_allow_html=True)
        
        if st.session_state["wybrane_konto"] is None:
            st.markdown('<p style="text-align:center; font-size:1.1rem; color:#cbd5e1; margin-bottom:30px;">Zidentyfikuj swój profil operatora</p>', unsafe_allow_html=True)
            cols = st.columns(3)
            for i, uz in enumerate(lista_uz):
                login = str(uz["Login"])
                rola = str(uz.get("Rola", ""))
                icon = "👨‍💼" if rola == "Admin" else "🚚" if rola == "Kierowca" else "🏭" if rola == "Magazyn" else "👤"
                
                with cols[i % 3]:
                    if st.button(f"{icon}\n\n{login}", key=f"login_{login}", use_container_width=True):
                        st.session_state["wybrane_konto"] = login
                        st.rerun()
        else:
            wybrane_konto = st.session_state["wybrane_konto"]
            dane_konta = next((u for u in lista_uz if str(u["Login"]) == wybrane_konto), None)
            
            st.markdown(f'<p style="text-align:center; color: #38bdf8; font-weight: bold; font-size: 1.2rem; margin-bottom: 25px;">Konto operatora: {wybrane_konto}</p>', unsafe_allow_html=True)
            pin = st.text_input("Wprowadź Kod PIN", type="password", placeholder="****")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔙 Zmień profil", use_container_width=True):
                    st.session_state["wybrane_konto"] = None
                    st.rerun()
            with c2:
                if st.button("Zaloguj", type="primary", use_container_width=True):
                    if dane_konta and str(dane_konta["PIN"]) == pin:
                        st.session_state["zalogowany"] = wybrane_konto
                        st.session_state["rola"] = str(dane_konta.get("Rola", "Admin"))
                        st.session_state["blokada_autologowania"] = False
                        
                        ts = str(int(time.time() * 1000))
                        cookie_manager.set("zalogowany", wybrane_konto, expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key=f"set_log_{ts}")
                        wczytaj_ustawienia_z_bazy(wybrane_konto)
                        st.session_state["ustawienia_wczytane"] = True
                        st.rerun()
                    else:
                        st.error("Błąd autoryzacji.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🌌 CENTRALNY PANEL OPERACYJNY ( HUD + VIEWPORT )
# ==========================================
else:
    uzytkownik = st.session_state["zalogowany"]
    rola = st.session_state.get("rola", "Admin")

    # Twarde upewnienie się, że ustawienia są poprawne (np. po wciśnięciu F5)
    if not st.session_state["ustawienia_wczytane"]:
        wczytaj_ustawienia_z_bazy(uzytkownik)
        st.session_state["ustawienia_wczytane"] = True
    
    # --- CYFROWY TOP-BAR SYSTEMOWY ---
    col_logo, col_time, col_user, col_logout = st.columns([2.5, 4.5, 2, 1])
    with col_logo:
        st.markdown(f'<div class="system-brand">SQM CONTROL TOWER <span class="system-status-pill">{rola.upper()}</span></div>', unsafe_allow_html=True)
    with col_time:
        teraz_str = datetime.datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%H:%M:%S")
        st.markdown(f'<div class="system-clock">CZAS OPERACYJNY | {teraz_str} PL</div>', unsafe_allow_html=True)
    with col_user:
        st.markdown(f'<div class="system-user-tag">Operator: <b>{uzytkownik}</b></div>', unsafe_allow_html=True)
    with col_logout:
        if st.button("⏻", key="btn_logout", help="Bezpieczne wylogowanie z systemu", use_container_width=True):
            ts = str(int(time.time() * 1000))
            try: 
                cookie_manager.set("zalogowany", "", expires_at=datetime.datetime.now() - datetime.timedelta(days=1), key=f"del_log_{ts}")
                cookie_manager.delete("zalogowany", key=f"del_log2_{ts}")
            except: pass
            
            st.session_state["zalogowany"] = None
            st.session_state["rola"] = None
            st.session_state["wybrane_konto"] = None
            st.session_state["ustawienia_wczytane"] = False
            st.session_state["aktywny_modul"] = "Control Tower"
            st.session_state["blokada_autologowania"] = True
            
            time.sleep(0.3)
            st.rerun()

    st.markdown("<div class='system-divider'></div>", unsafe_allow_html=True)

    # --- ROUTING I WIDOKI DLA ADMINISTRATORA ---
    if rola == "Admin":
        st_autorefresh(interval=60000, key="auto_ref_admin")
        
        df_dzis = data_processing.pobierz_dane_na_dzien()
        total_tasks = len(df_dzis)
        in_transit = len(df_dzis[df_dzis['Status'] == 'W drodze']) if not df_dzis.empty else 0
        pending_warehouse = len(df_dzis[df_dzis['Status'].isin(['Nowe', 'Zaakceptowane', 'Awizacja'])]) if not df_dzis.empty else 0

        st.markdown('<span id="main-workspace"></span>', unsafe_allow_html=True)
        col_hud, col_viewport = st.columns([3, 7])
        
        with col_hud:
            st.markdown('<div class="hud-section-title">📊 TELEMETRIA FLOTY</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="hud-metric-container">
                <div class="hud-metric-card border-blue"><h5>ZLECENIA DZIŚ</h5><h4>{total_tasks}</h4></div>
                <div class="hud-metric-card border-green"><h5>W TRASIE</h5><h4>{in_transit}</h4></div>
                <div class="hud-metric-card border-orange"><h5>AWIZACJE</h5><h4>{pending_warehouse}</h4></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="hud-section-title" style="margin-top:25px;">🛠️ SYSTEM INTERFEJSÓW</div>', unsafe_allow_html=True)
            
            opcje_modulow = [
                "📡 Widok Radaru (Control Tower)",
                "📊 Centrum Statystyk (Dashboard)",
                "➕ Rejestracja Zadań (Nowy Wpis)",
                "🏭 Zarządzanie Magazynem",
                "🗓️ Harmonogram Pracy (Kalendarz)",
                "🛠️ Konsola Szybkiej Edycji",
                "📂 Archiwum Cyfrowe Plików",
                "👥 Zarządzanie Personelem"
            ]
            
            mapowanie_nazw = {
                "📡 Widok Radaru (Control Tower)": "Control Tower",
                "📊 Centrum Statystyk (Dashboard)": "Dashboard",
                "➕ Rejestracja Zadań (Nowy Wpis)": "Nowy Wpis",
                "🏭 Zarządzanie Magazynem": "Magazyn",
                "🗓️ Harmonogram Pracy (Kalendarz)": "Kalendarz",
                "🛠️ Konsola Szybkiej Edycji": "Konsola Admin.",
                "📂 Archiwum Cyfrowe Plików": "Archiwum",
                "👥 Zarządzanie Personelem": "Użytkownicy"
            }
            
            wyszukaj_indeks = list(mapowanie_nazw.values()).index(st.session_state["aktywny_modul"]) if st.session_state["aktywny_modul"] in mapowanie_nazw.values() else 0
            
            wybor_hud = st.radio("Nawigacja Taktyczna", opcje_modulow, index=wyszukaj_indeks, label_visibility="collapsed")
            st.session_state["aktywny_modul"] = mapowanie_nazw[wybor_hud]
            
            with st.expander("🎨 Parametry wizualne powłoki"):
                def aktualizuj_ustawienia():
                    st.session_state["bg_opacity"] = st.session_state["suwak_opacity"]
                    st.session_state["bg_blur"] = st.session_state["suwak_blur"]

                st.slider("Przezroczystość", 0.0, 1.0, step=0.05, key="suwak_opacity", on_change=aktualizuj_ustawienia)
                st.slider("Współczynnik Blur", 0, 20, step=1, key="suwak_blur", on_change=aktualizuj_ustawienia)
                
                if st.button("💾 Zapamiętaj ustawienia", use_container_width=True):
                    # Zapis do Google Sheets
                    database.zapisz_ustawienia_uzytkownika(uzytkownik, st.session_state.suwak_opacity, st.session_state.suwak_blur)
                    # Wymuszenie twardego przeładowania zmiennych żeby zabić stany z poprzednich sesji
                    wczytaj_ustawienia_z_bazy(uzytkownik)
                    st.toast("✅ Konfiguracja powłoki trwale zapisana w Google Sheets!")
                    st.rerun()
            
        with col_viewport:
            if st.session_state["aktywny_modul"] == "Control Tower": ui_mapa.pokaz_mape()
            elif st.session_state["aktywny_modul"] == "Dashboard": ui_lukasz.pokaz_dashboard()
            elif st.session_state["aktywny_modul"] == "Nowy Wpis": ui_lukasz.pokaz_formularz()
            elif st.session_state["aktywny_modul"] == "Kalendarz": ui_kalendarz.pokaz_kalendarz()
            elif st.session_state["aktywny_modul"] == "Magazyn": ui_lukasz.pokaz_magazyn()
            elif st.session_state["aktywny_modul"] == "Konsola Admin.": ui_lukasz.pokaz_zarzadzanie()
            elif st.session_state["aktywny_modul"] == "Archiwum": ui_lukasz.pokaz_archiwum()
            elif st.session_state["aktywny_modul"] == "Użytkownicy": ui_uzytkownicy.pokaz_panel_uzytkownikow()

    elif rola == "Kierowca":
        _, col_mob, _ = st.columns([1, 2, 1])
        with col_mob: ui_dawid.pokaz_panel() 
    
    else: 
        st_autorefresh(interval=30000, key="auto_ref_mag")
        ui_magazyn.pokaz_tablice()
