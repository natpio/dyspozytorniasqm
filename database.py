import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_gspread_client():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.authorize(credentials)

def get_worksheet(nazwa_arkusza="Arkusz1"):
    gc = get_gspread_client()
    return gc.open("AplikacjaKasprzak").worksheet(nazwa_arkusza)

def pobierz_wszystkie_dane():
    return get_worksheet("Arkusz1").get_all_records()

def dodaj_zadanie(wiersz):
    get_worksheet("Arkusz1").append_row(wiersz)

def aktualizuj_status(id_zadania, nowy_status):
    arkusz = get_worksheet("Arkusz1")
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        arkusz.update_cell(komorka.row, 11, nowy_status) # 11 to kolumna 'Status'

def usun_zadanie(id_zadania):
    arkusz = get_worksheet("Arkusz1")
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        arkusz.delete_rows(komorka.row)

def archiwizuj_zadanie(id_zadania):
    arkusz = get_worksheet("Arkusz1")
    archiwum = get_worksheet("Archiwum")
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        wiersz = arkusz.row_values(komorka.row)
        archiwum.append_row(wiersz)
        arkusz.delete_rows(komorka.row)

def edytuj_zadanie(id_zadania, nowy_wiersz):
    arkusz = get_worksheet("Arkusz1")
    komorka = arkusz.find(str(id_zadania))
    if komorka:
        # Zapisujemy komórkę po komórce dla bezpieczeństwa typu danych
        lista_komorek = arkusz.range(f"A{komorka.row}:L{komorka.row}")
        for i, wartosc in enumerate(nowy_wiersz):
            lista_komorek[i].value = str(wartosc)
        arkusz.update_cells(lista_komorek)
