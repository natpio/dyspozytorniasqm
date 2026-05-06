import streamlit as st
from streamlit_autorefresh import st_autorefresh
import ui_lukasz
import ui_dawid

st.set_page_config(page_title="SQM App - Logistyka", layout="wide")

# Inicjalizacja sesji logowania
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

# EKRAN LOGOWANIA
if st.session_state["zalogowany"] is None:
    st.title("🔐 Logowanie do systemu SQM")
    st.write("Wprowadź swój PIN, aby uzyskać dostęp.")
    
    col1, col2 = st.columns([1, 3])
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

# EKRAN PO ZALOGOWANIU
else:
    uzytkownik = st.session_state["zalogowany"]
    
    col_tytul, col_wyloguj = st.columns([5, 1])
    with col_tytul:
        st.title(f"🚚 System Logistyki SQM - Panel: {uzytkownik}")
    with col_wyloguj:
        if st.button("🚪 Wyloguj"):
            st.session_state["zalogowany"] = None
            st.rerun()
    
    # Widok dla Łukasza
    if uzytkownik == "Łukasz":
        # Odświeżanie co 30 000 milisekund (30 sekund)
        st_autorefresh(interval=30000, limit=None, key="odswiezanie_lukasz")
        
        tab1, tab2 = st.tabs(["📝 Dodaj Zadanie", "📊 Baza i Zarządzanie (Edycja)"])
        with tab1:
            ui_lukasz.pokaz_formularz()
        with tab2:
            ui_lukasz.pokaz_tabele_i_zarzadzanie()
            
    # Widok dla Dawida
    elif uzytkownik == "Dawid":
        ui_dawid.pokaz_panel()
