import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_google_sheet():
    """Zwraca połączenie z arkuszem."""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=SCOPES
    )
    gc = gspread.authorize(credentials)
    return gc.open("AplikacjaKasprzak").worksheet("Arkusz1")

def pobierz_wszystkie_dane():
    """Pobiera wszystkie wiersze z arkusza."""
    arkusz = get_google_sheet()
    return arkusz.get_all_records()

def dodaj_zadanie(wiersz):
    """Dodaje nowy wiersz do arkusza."""
    arkusz = get_google_sheet()
    arkusz.append_row(wiersz)

def aktualizuj_status(id_zadania, nowy_status):
    """Zmienia status dla podanego ID zadania."""
    arkusz = get_google_sheet()
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        arkusz.update_cell(komorka.row, 11, nowy_status) # 11 to kolumna 'Status'
