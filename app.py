import streamlit as st
import ui_lukasz
import ui_dawid

# Konfiguracja strony musi być w głównym pliku, jako pierwsza komenda
st.set_page_config(page_title="SQM App - Logistyka", layout="wide")

st.title("🚚 System Logistyki SQM")

# Tworzymy zakładki
tab1, tab2, tab3 = st.tabs(["📝 Dodaj Zadanie (Łukasz)", "📊 Baza Zadań", "📱 Panel Kierowcy (Dawid)"])

# Wywołujemy funkcje z naszych nowych modułów!
with tab1:
    ui_lukasz.pokaz_formularz()
    
with tab2:
    ui_lukasz.pokaz_tabele()
    
with tab3:
    ui_dawid.pokaz_panel()
