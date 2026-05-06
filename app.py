import streamlit as st
from streamlit_autorefresh import st_autorefresh
import ui_lukasz
import ui_dawid

# --- KONFIGURACJA STRONY (Musi być pierwsza) ---
st.set_page_config(page_title="SQM Dispatch", layout="wide", initial_sidebar_state="expanded")

# --- STYLE CSS (Dark Mode & Glassmorphism) ---
st.markdown("""
<style>
/* Tło główne całej aplikacji */
.stApp {
    background-color: #0d1117; 
}
/* Stylowanie kart KPI u Łukasza */
div.kpi-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    text-align: left;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
div.kpi-title {
    font-size: 0.9rem;
    color: #8b949e;
    margin-bottom: 10px;
    font-weight: 500;
}
div.kpi-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #e6edf3;
}
</style>
""", unsafe_allow_html=True)

# Inicjalizacja sesji logowania
if "zalogowany" not in st.session_state:
    st.session_state["zalogowany"] = None

# EKRAN LOGOWANIA
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

# EKRAN PO ZALOGOWANIU
else:
    uzytkownik = st.session_state["zalogowany"]
    
    # --- LEWY PASEK NAWIGACYJNY (SIDEBAR) ---
    with st.sidebar:
        st.markdown("### 📦 SQM DISPATCH")
        st.write(f"Zalogowano jako: **{uzytkownik}**")
        st.markdown("---")
        
        if uzytkownik == "Łukasz":
            st.markdown("GŁÓWNE")
            menu = st.radio("Menu Główne", ["🏠 Dashboard", "📝 Nowe Zlecenie"], label_visibility="collapsed")
            st.markdown("OPERACJE")
            menu2 = st.radio("Menu Operacje", ["⚙️ Zarządzanie Bazą"], label_visibility="collapsed")
            
            wybor = menu if menu in ["🏠 Dashboard", "📝 Nowe Zlecenie"] else menu2
            
        elif uzytkownik == "Dawid":
            wybor = st.radio("Menu", ["📱 Moje Zlecenia", "🗺️ Mapa (Wkrótce)"])
        
        st.markdown("---")
        if st.button("🚪 Wyloguj się", use_container_width=True):
            st.session_state["zalogowany"] = None
            st.rerun()

    # --- ROUTING (Przekierowania do odpowiednich ekranów) ---
    if uzytkownik == "Łukasz":
        st_autorefresh(interval=30000, limit=None, key="odswiezanie_lukasz")
        
        if wybor == "🏠 Dashboard":
            ui_lukasz.pokaz_dashboard()
        elif wybor == "📝 Nowe Zlecenie":
            ui_lukasz.pokaz_formularz()
        elif wybor == "⚙️ Zarządzanie Bazą":
            ui_lukasz.pokaz_zarzadzanie()
            
    elif uzytkownik == "Dawid":
        if wybor == "📱 Moje Zlecenia":
            ui_dawid.pokaz_panel()
        else:
            st.info("Moduł Mapy w przygotowaniu...")
