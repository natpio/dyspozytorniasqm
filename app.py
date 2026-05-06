import streamlit as st
from streamlit_autorefresh import st_autorefresh
import ui_lukasz
import ui_dawid

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="SQM Dispatch", layout="wide", initial_sidebar_state="expanded")

# --- STYLE CSS ---
st.markdown("""
<style>
div.kpi-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #eef0f4;
    text-align: left;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
}
div.kpi-title {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 5px;
    font-weight: 500;
}
div.kpi-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0f172a;
}
[data-testid="stSidebar"] {
    background-color: #0b1120 !important;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

# LOGOWANIE
if st.session_state["zalogowany"] is None:
    st.title("🔐 SQM Dispatch - Logowanie")
    col1, col2 = st.columns([1, 3])
    with col1:
        pin = st.text_input("Kod PIN", type="password")
        if st.button("Zaloguj", type="primary", use_container_width=True):
            if pin == "1234":
                st.session_state["zalogowany"] = "Łukasz"
                st.rerun()
            elif pin == "5678":
                st.session_state["zalogowany"] = "Dawid"
                st.rerun()
            else:
                st.error("Błędny PIN!")

# PO ZALOGOWANIU
else:
    uzytkownik = st.session_state["zalogowany"]
    
    with st.sidebar:
        st.markdown("### 📦 SQM DISPATCH")
        st.write(f"Zalogowano jako: **{uzytkownik}**")
        st.markdown("---")
        
        if uzytkownik == "Łukasz":
            st.markdown("**MENU**")
            # TUTAJ MUSZĄ BYĆ 4 OPCJE:
            wybor = st.radio("Nawigacja", [
                "🏠 Dashboard", 
                "📝 Nowe Zlecenie", 
                "⚙️ Zarządzanie Bazą",
                "📦 Archiwum"
            ], label_visibility="collapsed")
            
        elif uzytkownik == "Dawid":
            st.markdown("**MENU**")
            wybor = st.radio("Nawigacja", [
                "📱 Moje Zlecenia", 
                "🗺️ Mapa"
            ], label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("🚪 Wyloguj się", use_container_width=True):
            st.session_state["zalogowany"] = None
            st.rerun()

    # ROUTING
    if uzytkownik == "Łukasz":
        st_autorefresh(interval=30000, limit=None, key="odswiezanie_lukasz")
        
        if wybor == "🏠 Dashboard":
            ui_lukasz.pokaz_dashboard()
        elif wybor == "📝 Nowe Zlecenie":
            ui_lukasz.pokaz_formularz()
        elif wybor == "⚙️ Zarządzanie Bazą":
            ui_lukasz.pokaz_zarzadzanie()
        elif wybor == "📦 Archiwum":
            ui_lukasz.pokaz_archiwum()
            
    elif uzytkownik == "Dawid":
        if wybor == "📱 Moje Zlecenia":
            ui_dawid.pokaz_panel()
        else:
            st.info("Moduł Mapy w przygotowaniu...")
