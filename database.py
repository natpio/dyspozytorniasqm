import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Definiowanie uprawnień do Google Sheets i Google Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
    """Inicjalizuje i zwraca połączenie z Google Sheets na podstawie st.secrets."""
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=SCOPES
    )
    return gspread.authorize(credentials)

def get_worksheet(nazwa_arkusza="Arkusz1"):
    """Pobiera konkretny arkusz z naszego pliku bazy danych."""
    gc = get_gspread_client()
    return gc.open("AplikacjaKasprzak").worksheet(nazwa_arkusza)

def pobierz_wszystkie_dane():
    """Pobiera wszystkie aktywne zadania z głównego arkusza."""
    return get_worksheet("Arkusz1").get_all_records()

def pobierz_archiwum():
    """Pobiera wszystkie zarchiwizowane zadania z zakładki Archiwum."""
    return get_worksheet("Archiwum").get_all_records()

def dodaj_zadanie(wiersz):
    """Dodaje nowy wiersz z zadaniem na koniec głównego arkusza."""
    get_worksheet("Arkusz1").append_row(wiersz)

def aktualizuj_status(id_zadania, nowy_status):
    """Aktualizuje status wybranego zadania (kolumna 11 to 'Status')."""
    arkusz = get_worksheet("Arkusz1")
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        arkusz.update_cell(komorka.row, 11, nowy_status)

def usun_zadanie(id_zadania):
    """Usuwa całkowicie wiersz z zadaniem z bazy."""
    arkusz = get_worksheet("Arkusz1")
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        arkusz.delete_rows(komorka.row)

def archiwizuj_zadanie(id_zadania):
    """Przenosi wiersz z głównego arkusza do zakładki 'Archiwum'."""
    arkusz = get_worksheet("Arkusz1")
    archiwum = get_worksheet("Archiwum")
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        # Kopiowanie danych wiersza
        wiersz = arkusz.row_values(komorka.row)
        # Wklejenie do archiwum
        archiwum.append_row(wiersz)
        # Usunięcie z głównego widoku
        arkusz.delete_rows(komorka.row)

def edytuj_zadanie(id_zadania, nowy_wiersz):
    """Zastępuje dane wiersza nowymi wartościami na podstawie ID."""
    arkusz = get_worksheet("Arkusz1")
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        # Pobieramy zakres komórek dla danego wiersza (zakładamy kolumny od A do L)
        lista_komorek = arkusz.range(f"A{komorka.row}:L{komorka.row}")
        for i, wartosc in enumerate(nowy_wiersz):
            lista_komorek[i].value = str(wartosc)
        # Zbiorcza aktualizacja komórek (szybsze i bezpieczniejsze niż pojedynczo)
        arkusz.update_cells(lista_komorek)
