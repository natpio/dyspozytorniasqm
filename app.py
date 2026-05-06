import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="SQM App - Dyspozytornia", layout="wide")

# --- POŁĄCZENIE Z BAZĄ (Zostaje bez zmian, używamy cache dla szybkości) ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_google_sheet():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=scopes
    )
    gc = gspread.authorize(credentials)
    return gc.open("AplikacjaKasprzak").worksheet("Arkusz1")

arkusz = get_google_sheet()

# --- INTERFEJS GŁÓWNY ---
st.title("🚚 System Zarządzania Zadaniami SQM")

# Tworzymy zakładki w aplikacji
tab1, tab2 = st.tabs(["📝 Dodaj Zadanie (Panel Łukasza)", "📊 Baza Wszystkich Zadań"])

# --- ZAKŁADKA 1: FORMULARZ DODAWANIA ---
with tab1:
    st.header("Dodaj nowe zadanie")
    
    with st.form("nowe_zadanie_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            data = st.date_input("Data realizacji")
            godzina = st.time_input("Godzina")
            dzial = st.selectbox("Dział", ["Rental", "Realizacja"])
            typ_akcji = st.selectbox("Typ Akcji", [
                "Dowóz do klienta", 
                "Odbiór od klienta", 
                "Magazyn - Odbiór osobisty przez klienta", 
                "Magazyn - Zwrot osobisty przez klienta"
            ])
            auto = st.selectbox("Auto", ["Brak", "Bus 1 (Renault)", "Bus 2 (Peugeot)"]) # Możesz tu wpisać swoje auta
            
        with col2:
            nr_projektu = st.text_input("Nr Projektu (opcjonalnie)")
            klient = st.text_input("Klient")
            lokalizacja = st.text_input("Lokalizacja (adres - zostaw puste dla magazynu)")
            kontakt = st.text_input("Kontakt (Imię / Telefon)")

        # Przycisk wysyłający formularz
        submit_button = st.form_submit_button("Zapisz Zadanie", type="primary")

        if submit_button:
            # 1. Generowanie unikalnego ID (np. 202310241530)
            id_zadania = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # 2. Inteligentne przypisanie wykonawcy i statusu
            if "Magazyn" in typ_akcji:
                wykonawca = "Łukasz (Magazyn)"
                status = "Awizacja" # Dla Łukasza to tylko informacja, że ktoś przyjedzie
            else:
                wykonawca = "Dawid"
                status = "Nowe" # Dawid będzie musiał to zaakceptować

            # 3. Złożenie wiersza danych do wysłania do Google Sheets
            nowy_wiersz = [
                id_zadania, 
                data.strftime("%Y-%m-%d"), 
                godzina.strftime("%H:%M"), 
                dzial, 
                typ_akcji, 
                nr_projektu, 
                klient, 
                lokalizacja, 
                kontakt, 
                auto, 
                status, 
                wykonawca
            ]
            
            # 4. Zapis do arkusza i komunikat
            try:
                arkusz.append_row(nowy_wiersz)
                st.success(f"Zadanie dla {klient} zostało poprawnie dodane do bazy! Wykonawca: {wykonawca}")
            except Exception as e:
                st.error(f"Wystąpił błąd podczas zapisywania: {e}")

# --- ZAKŁADKA 2: PODGLĄD DANYCH ---
with tab2:
    st.header("Podgląd bazy danych")
    st.info("Poniżej widzisz wszystkie dane z Google Sheets. Kliknij 'Odśwież dane' aby pobrać najnowsze zmiany.")
    
    if st.button("Odśwież dane"):
        st.cache_resource.clear() # Czyści pamięć podręczną, aby pobrać świeże dane
        st.rerun()

    dane = arkusz.get_all_records()
    if dane:
        df = pd.DataFrame(dane)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Brak zadań w bazie. Dodaj pierwsze zadanie w zakładce obok!")
