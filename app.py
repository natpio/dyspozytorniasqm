import streamlit as st
import extra_streamlit_components as stx
from streamlit_autorefresh import st_autorefresh
import datetime
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
import config

# --- 1. KONFIGURACJA STRONY (Maksymalne wykorzystanie przestrzeni) ---
st.set_page_config(layout="wide", page_title="SQM CONTROL TOWER OS", page_icon="📍", initial_sidebar_state="collapsed")

# --- 2. PERSYSTENCJA SESJI (Ciasteczka) ---
cookie_manager = stx.CookieManager(key="sqm_control_tower_v90")

# --- 3. INICJALIZACJA STANÓW SYSTEMOWYCH ---
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
if "aktywny_modul" not in st.session_state:
    st.session_state["aktywny_modul"] = "Control Tower"

def pobierz_role_z_bazy(login):
    uzytkownicy = database.pobierz_uzytkownikow()
    for u in uzytkownicy:
        if str(u.get("Login", "")) == login:
            return str(u.get("Rola", ""))
    return "Admin"

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
        op, bl = database.pobierz_ustawienia_uzytkownika(uzytkownik)
        op_str = str(op).replace(',', '.').strip()
        bl_str = str(bl).replace(',', '.').strip()
        st.session_state["bg_opacity"] = max(0.0, min(1.0, float(op_str if op_str != 'None' else 0.55)))
        st.session_state["bg_blur"] = max(0, min(20, int(float(bl_str if bl_str != 'None' else 12))))
    except:
        st.session_state["bg_opacity"] = 0.55
        st.session_state["bg_blur"] = 12

# --- AUTOLOGOWANIE ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")
if zalogowany_cookie and not st.session_state["ustawienia_wczytane"] and not st.session_state["blokada_autologowania"]:
    st.session_state["zalogowany"] = zalogowany_cookie
    st.session_state["rola"] = pobierz_role_z_bazy(zalogowany_cookie)
    wczytaj_ustawienia(zalogowany_cookie)
    st.session_state["ustawienia_wczytane"] = True
    st.rerun()

if "bg_opacity" not in st.session_state: st.session_state.bg_opacity = 0.55
if "bg_blur" not in st.session_state: st.session_state.bg_blur = 12

# --- INIEKCJA STYLÓW SYSTEMOWYCH ---
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
                        
                        # ZDEJMUJEMY BLOKADĘ po poprawnym, ręcznym zalogowaniu
                        st.session_state["blokada_autologowania"] = False
                        
                        ts = str(int(time.time() * 1000))
                        cookie_manager.set("zalogowany", wybrane_konto, expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key=f"set_log_{ts}")
                        wczytaj_ustawienia(wybrane_konto)
                        st.session_state["ustawienia_wczytane"] = True
                        st.rerun()
                    else:
                        st.error("Błąd autoryzacji.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🌌 PANEL RADAROWY CONTROL TOWER (PO ZALOGOWANIU)
# ==========================================
else:
    uzytkownik = st.session_state["zalogowany"]
    rola = st.session_state.get("rola", "Admin")
    
    # --- CYFROWY TOP-BAR SYSTEMOWY ---
    col_logo, col_time, col_user, col_logout = st.columns([2.5, 4.5, 2, 1])
    with col_logo:
        st.markdown(f'<div class="system-brand">SQM CONTROL TOWER <span class="system-status-pill">{rola.upper()}</span></div>', unsafe_allow_html=True)
    with col_time:
        teraz_str = datetime.datetime.now().strftime("%H:%M:%S [CET]")
        st.markdown(f'<div class="system-clock">📡 RADAR LIVE | {teraz_str}</div>', unsafe_allow_html=True)
    with col_user:
        st.markdown(f'<div class="system-user-tag">Operator: <b>{uzytkownik}</b></div>', unsafe_allow_html=True)
    with col_logout:
        if st.button("⏻", key="btn_logout", help="Bezpieczne wylogowanie z systemu", use_container_width=True):
            ts = str(int(time.time() * 1000))
            try: 
                # Nadpisujemy ciasteczko pustą wartością ze wsteczną datą ważności
                cookie_manager.set("zalogowany", "", expires_at=datetime.datetime.now() - datetime.timedelta(days=1), key=f"del_log_{ts}")
                cookie_manager.delete("zalogowany", key=f"del_log2_{ts}")
            except: pass
            
            # Bezpieczne czyszczenie stanów konta bez niszczenia flagi blokady autologowania
            st.session_state["zalogowany"] = None
            st.session_state["rola"] = None
            st.session_state["wybrane_konto"] = None
            st.session_state["ustawienia_wczytane"] = False
            st.session_state["aktywny_modul"] = "Control Tower"
            
            # AKTYWACJA BLOKADY - Zapobiega ponownemu przechwyceniu sesji przez stare ciasteczko
            st.session_state["blokada_autologowania"] = True
            
            # Czyszczenie pamięci menu bocznego przy wylogowaniu
            if "hud_radio_key" in st.session_state: del st.session_state["hud_radio_key"]
            
            time.sleep(0.3)
            st.rerun()

    st.markdown("<div class='system-divider'></div>", unsafe_allow_html=True)

    # --- ARCHITEKTURA WIDOKÓW DLA ADMINISTRATORA ---
    if rola == "Admin":
        st_autorefresh(interval=60000, key="auto_ref_admin")
        
        # --- AGREGACJA METRYK OPERACYJNYCH DLA PANELU HUD ---
        dane_baza = database.pobierz_wszystkie_dane()
        df_baza = pd.DataFrame(dane_baza) if dane_baza else pd.DataFrame()
        dzis_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if not df_baza.empty and 'Data' in df_baza.columns:
            df_dzis = df_baza[df_baza['Data'] == dzis_str]
            total_tasks = len(df_dzis)
            in_transit = len(df_dzis[df_dzis['Status'] == 'W drodze']) if 'Status' in df_dzis.columns else 0
            pending_warehouse = len(df_dzis[df_dzis['Status'].isin(['Nowe', 'Zaakceptowane', 'Awizacja'])]) if 'Status' in df_dzis.columns else 0
        else:
            total_tasks, in_transit, pending_warehouse = 0, 0, 0

        # BUDOWA DWUKOLUMNOWEGO KOKPITU CONTROL TOWER
        col_hud, col_viewport = st.columns([3, 7])
        
        # --- LEWY PANEL: HUD (NAWIGACJA + METRYKI LIVE) ---
        with col_hud:
            st.markdown('<div class="hud-wrapper">', unsafe_allow_html=True)
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
            
            # Bezpieczna funkcja callback nawigacji - gwarantuje nadpisanie stanu przed przeładowaniem viewportu
            def aktualizuj_modul():
                wybrany_label = st.session_state["hud_radio_key"]
                st.session_state["aktywny_modul"] = mapowanie_nazw[wybrany_label]
            
            # Kotwiczenie menu za pomocą klucza i funkcji on_change
            st.radio(
                "Nawigacja Taktyczna", 
                opcje_modulow, 
                index=wyszukaj_indeks, 
                key="hud_radio_key",
                on_change=aktualizuj_modul,
                label_visibility="collapsed"
            )
            
            with st.expander("🎨 Parametry wizualne powłoki"):
                # Definicja bezpiecznych funkcji callback do aktualizacji stanu suwaków
                def aktualizuj_opacity():
                    st.session_state["bg_opacity"] = st.session_state["suwak_opacity"]
                
                def aktualizuj_blur():
                    st.session_state["bg_blur"] = st.session_state["suwak_blur"]

                # Izolacja suwaków przed resetami w tle za pomocą dedykowanych kluczy (suwak_...)
                st.slider(
                    "Przezroczystość", 0.0, 1.0, 
                    value=float(st.session_state.get("bg_opacity", 0.55)), 
                    step=0.05, 
                    key="suwak_opacity", 
                    on_change=aktualizuj_opacity
                )
                st.slider(
                    "Współczynnik Blur", 0, 20, 
                    value=int(st.session_state.get("bg_blur", 12)), 
                    step=1, 
                    key="suwak_blur", 
                    on_change=aktualizuj_blur
                )
                
                if st.button("💾 Zapamiętaj ustawienia", use_container_width=True):
                    database.zapisz_ustawienia_uzytkownika(uzytkownik, st.session_state.bg_opacity, st.session_state.bg_blur)
                    ts = str(int(time.time() * 1000))
                    cookie_manager.set(f"ui_op_{uzytkownik}", str(st.session_state.bg_opacity), expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key=f"s_op_{ts}")
                    cookie_manager.set(f"ui_bl_{uzytkownik}", str(st.session_state.bg_blur), expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key=f"s_bl_{ts}")
                    st.toast("Konfiguracja warstwy szklanej zapisana!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        # --- PRAWY PANEL: MATRYCA INTERFEJSU (VIEWPORT) ---
        with col_viewport:
            st.markdown('<div class="viewport-wrapper">', unsafe_allow_html=True)
            
            if st.session_state["aktywny_modul"] == "Control Tower":
                ui_mapa.pokaz_mape()
            elif st.session_state["aktywny_modul"] == "Dashboard": 
                ui_lukasz.pokaz_dashboard()
            elif st.session_state["aktywny_modul"] == "Nowy Wpis": 
                ui_lukasz.pokaz_formularz()
            elif st.session_state["aktywny_modul"] == "Kalendarz": 
                ui_kalendarz.pokaz_kalendarz()
            elif st.session_state["aktywny_modul"] == "Magazyn": 
                ui_lukasz.pokaz_magazyn()
            elif st.session_state["aktywny_modul"] == "Konsola Admin.": 
                ui_lukasz.pokaz_zarzadzanie()
            elif st.session_state["aktywny_modul"] == "Archiwum": 
                ui_lukasz.pokaz_archiwum()
            elif st.session_state["aktywny_modul"] == "Użytkownicy": 
                ui_uzytkownicy.pokaz_panel_uzytkownikow()
                
            st.markdown('</div>', unsafe_allow_html=True)

    # --- ROUTING DLA OPERATORÓW POZA PANELEM ADMINA ---
    elif rola == "Kierowca":
        _, col_mob, _ = st.columns([1, 2, 1])
        with col_mob:
            ui_dawid.pokaz_panel() 
    
    else: 
        st_autorefresh(interval=30000, key="auto_ref_mag")
        ui_magazyn.pokaz_tablice()
