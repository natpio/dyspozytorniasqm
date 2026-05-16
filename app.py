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
st.set_page_config(layout="wide", page_title="SQM DISPATCH OS", page_icon="📦", initial_sidebar_state="collapsed")

# --- 2. OBSŁUGA CIASTECZEK ---
cookie_manager = stx.CookieManager(key="sqm_dispatch_v80_premium_os")

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
if "aktywny_modul" not in st.session_state:
    st.session_state["aktywny_modul"] = "Menu Główne"

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
        st.session_state["bg_opacity"] = max(0.0, min(1.0, float(op_str if op_str != 'None' else 0.75)))
        st.session_state["bg_blur"] = max(0, min(20, int(float(bl_str if bl_str != 'None' else 4))))
    except:
        st.session_state["bg_opacity"] = 0.75
        st.session_state["bg_blur"] = 4

# --- AUTOLOGOWANIE ---
zalogowany_cookie = cookie_manager.get(cookie="zalogowany")
if zalogowany_cookie and not st.session_state["ustawienia_wczytane"] and not st.session_state["blokada_autologowania"]:
    st.session_state["zalogowany"] = zalogowany_cookie
    st.session_state["rola"] = pobierz_role_z_bazy(zalogowany_cookie)
    wczytaj_ustawienia(zalogowany_cookie)
    st.session_state["ustawienia_wczytane"] = True
    st.rerun()

if "bg_opacity" not in st.session_state: st.session_state.bg_opacity = 0.75
if "bg_blur" not in st.session_state: st.session_state.bg_blur = 4

# --- STYLE CSS ---
style.zastosuj_style(st.session_state.bg_opacity, st.session_state.bg_blur)

# ==========================================
# EKRAN LOGOWANIA
# ==========================================
if st.session_state["zalogowany"] is None:
    lista_uz = database.pobierz_uzytkownikow()
    if not lista_uz:
        lista_uz = [{"Login": "Piotr", "PIN": "1234", "Rola": "Admin"}]

    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1 style="margin-bottom: 10px; text-align:center; letter-spacing: -1px; color:#f8fafc;">🚀 SQM OS</h1>', unsafe_allow_html=True)
        
        if st.session_state["wybrane_konto"] is None:
            st.markdown('<p style="text-align:center; font-size:1.1rem; color:#cbd5e1; margin-bottom:30px;">Zidentyfikuj się</p>', unsafe_allow_html=True)
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
            
            st.markdown(f'<p style="text-align:center; color: #38bdf8; font-weight: bold; font-size: 1.2rem; margin-bottom: 25px;">Konto: {wybrane_konto}</p>', unsafe_allow_html=True)
            pin = st.text_input("Kod Autoryzacji", type="password", placeholder="****")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔙 Anuluj", use_container_width=True):
                    st.session_state["wybrane_konto"] = None
                    st.rerun()
            with c2:
                if st.button("Autoryzuj", type="primary", use_container_width=True):
                    if dane_konta and str(dane_konta["PIN"]) == pin:
                        st.session_state["zalogowany"] = wybrane_konto
                        st.session_state["rola"] = str(dane_konta.get("Rola", "Admin"))
                        ts = str(int(time.time() * 1000))
                        cookie_manager.set("zalogowany", wybrane_konto, expires_at=datetime.datetime.now() + datetime.timedelta(days=30), key=f"set_log_{ts}")
                        wczytaj_ustawienia(wybrane_konto)
                        st.session_state["ustawienia_wczytane"] = True
                        st.rerun()
                    else:
                        st.error("Błąd uwierzytelnienia.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# GŁÓWNY SYSTEM (PO ZALOGOWANIU)
# ==========================================
else:
    uzytkownik = st.session_state["zalogowany"]
    rola = st.session_state.get("rola", "Admin")
    
    # --- PŁYWAJĄCY PASEK NAWIGACYJNY (TOP-BAR) ---
    col_logo, col_space, col_user, col_logout = st.columns([2, 5, 2, 1])
    with col_logo:
        st.markdown(f'<div style="font-size:1.5rem; font-weight:900; color:#38bdf8; padding-top:5px; letter-spacing:-1px;">SQM OS <span style="font-size:0.8rem; color:#94a3b8; font-weight:normal;">| {rola.upper()}</span></div>', unsafe_allow_html=True)
    with col_user:
        st.markdown(f'<div style="text-align:right; padding-top:10px; color:#f8fafc; font-weight:bold;">👤 {uzytkownik}</div>', unsafe_allow_html=True)
    with col_logout:
        if st.button("⏻", key="btn_logout", help="Wyloguj się", use_container_width=True):
            ts = str(int(time.time() * 1000))
            try: cookie_manager.delete("zalogowany", key=f"del_log_{ts}")
            except: pass
            st.session_state.clear()
            st.rerun()

    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top:0px; margin-bottom:20px;'>", unsafe_allow_html=True)

    # --- ROUTING DLA ADMINA ---
    if rola == "Admin":
        st_autorefresh(interval=60000, key="auto_ref_admin")
        
        if st.session_state["aktywny_modul"] == "Menu Główne":
            # WIDOK KAFELKOWY
            st.markdown('<div style="text-align:center; margin-bottom: 40px;"><h2 style="color:white; font-weight:900;">Wybierz Moduł Operacyjny</h2></div>', unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("⚙️\nDashboard", key="m1", use_container_width=True): st.session_state["aktywny_modul"] = "Dashboard"; st.rerun()
                if st.button("🏭\nMagazyn", key="m5", use_container_width=True): st.session_state["aktywny_modul"] = "Magazyn"; st.rerun()
            with c2:
                if st.button("➕\nNowy Wpis", key="m2", use_container_width=True): st.session_state["aktywny_modul"] = "Nowy Wpis"; st.rerun()
                if st.button("📂\nArchiwum", key="m6", use_container_width=True): st.session_state["aktywny_modul"] = "Archiwum"; st.rerun()
            with c3:
                if st.button("📍\nMapa i Trasy", key="m3", use_container_width=True): st.session_state["aktywny_modul"] = "Mapa Routing"; st.rerun()
                if st.button("🛠️\nKonsola", key="m7", use_container_width=True): st.session_state["aktywny_modul"] = "Konsola Admin."; st.rerun()
            with c4:
                if st.button("🗓️\nKalendarz", key="m4", use_container_width=True): st.session_state["aktywny_modul"] = "Kalendarz"; st.rerun()
                if st.button("👥\nPersonel", key="m8", use_container_width=True): st.session_state["aktywny_modul"] = "Użytkownicy"; st.rerun()
            
            # Subtelne ustawienia na dole
            with st.expander("🎨 Ustawienia Interfejsu"):
                st.slider("Przezroczystość szkła", 0.0, 1.0, step=0.05, key="bg_opacity")
                st.slider("Rozmycie tła", 0, 20, step=1, key="bg_blur")
                if st.button("💾 Zapisz wygląd", use_container_width=True):
                    database.zapisz_ustawienia_uzytkownika(uzytkownik, st.session_state.bg_opacity, st.session_state.bg_blur)
                    cookie_manager.set(f"ui_op_{uzytkownik}", str(st.session_state.bg_opacity), expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                    cookie_manager.set(f"ui_bl_{uzytkownik}", str(st.session_state.bg_blur), expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                    st.toast("Zapisano wizualizację!")

        else:
            # WIDOK POJEDYNCZEGO MODUŁU Z PRZYCISKIEM POWROTU
            if st.button("⬅ Wróć do Menu Głównego", type="secondary"):
                st.session_state["aktywny_modul"] = "Menu Główne"
                st.rerun()
                
            if st.session_state["aktywny_modul"] == "Dashboard": ui_lukasz.pokaz_dashboard()
            elif st.session_state["aktywny_modul"] == "Nowy Wpis": ui_lukasz.pokaz_formularz()
            elif st.session_state["aktywny_modul"] == "Mapa Routing": ui_mapa.pokaz_mape()
            elif st.session_state["aktywny_modul"] == "Kalendarz": ui_kalendarz.pokaz_kalendarz()
            elif st.session_state["aktywny_modul"] == "Magazyn": ui_lukasz.pokaz_magazyn()
            elif st.session_state["aktywny_modul"] == "Konsola Admin.": ui_lukasz.pokaz_zarzadzanie()
            elif st.session_state["aktywny_modul"] == "Archiwum": ui_lukasz.pokaz_archiwum()
            elif st.session_state["aktywny_modul"] == "Użytkownicy": ui_uzytkownicy.pokaz_panel_uzytkownikow()

    # --- ROUTING DLA KIEROWCY ---
    elif rola == "Kierowca":
        _, col_mob, _ = st.columns([1, 2, 1])
        with col_mob:
            ui_dawid.pokaz_panel() 
    
    # --- ROUTING DLA MAGAZYNU ---
    else: 
        st_autorefresh(interval=30000, key="auto_ref_mag")
        ui_magazyn.pokaz_tablice()
