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

# --- FUNKCJE: OBSŁUGA ZADAŃ ---

def pobierz_wszystkie_dane():
    """Pobiera wszystkie aktywne zadania z głównego arkusza."""
    try:
        return get_worksheet("Arkusz1").get_all_records()
    except Exception as e:
        print(f"Błąd pobierania danych: {e}")
        return []

def pobierz_archiwum():
    """Pobiera wszystkie zarchiwizowane zadania z zakładki Archiwum."""
    try:
        return get_worksheet("Archiwum").get_all_records()
    except Exception as e:
        print(f"Błąd pobierania archiwum: {e}")
        return []

def dodaj_zadanie(wiersz):
    """Dodaje nowy wiersz z zadaniem na koniec głównego arkusza."""
    get_worksheet("Arkusz1").append_row(wiersz)

def aktualizuj_status(id_zadania, nowy_status):
    """Aktualizuje status wybranego zadania (kolumna 11 to 'Status')."""
    arkusz = get_worksheet("Arkusz1")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            arkusz.update_cell(komorka.row, 11, nowy_status)
    except Exception as e:
        pass

def usun_zadanie(id_zadania):
    """Usuwa całkowicie wiersz z zadaniem z bazy."""
    arkusz = get_worksheet("Arkusz1")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            arkusz.delete_rows(komorka.row)
    except Exception as e:
        pass

def archiwizuj_zadanie(id_zadania):
    """Przenosi wiersz z głównego arkusza do zakładki 'Archiwum'."""
    arkusz = get_worksheet("Arkusz1")
    archiwum = get_worksheet("Archiwum")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            wiersz = arkusz.row_values(komorka.row)
            archiwum.append_row(wiersz)
            arkusz.delete_rows(komorka.row)
    except Exception as e:
        pass

def edytuj_zadanie(id_zadania, nowy_wiersz):
    """Zastępuje dane wiersza nowymi wartościami na podstawie ID."""
    arkusz = get_worksheet("Arkusz1")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            lista_komorek = arkusz.range(f"A{komorka.row}:L{komorka.row}")
            for i, wartosc in enumerate(nowy_wiersz):
                lista_komorek[i].value = str(wartosc)
            arkusz.update_cells(lista_komorek)
    except Exception as e:
        pass

# --- FUNKCJE: OBSŁUGA USTAWIEŃ UI ---

def pobierz_ustawienia_uzytkownika(uzytkownik):
    """Pobiera opacity i blur dla konkretnego uzytkownika. Jesli brak, zwraca domyslne."""
    try:
        arkusz = get_worksheet("Ustawienia")
        rekordy = arkusz.get_all_records()
        for r in rekordy:
            if str(r.get('Uzytkownik', '')) == str(uzytkownik):
                return float(r.get('Opacity', 0.75)), int(r.get('Blur', 4))
    except Exception as e:
        print(f"Błąd pobierania ustawień: {e}")
        pass
    
    return 0.75, 4 

def zapisz_ustawienia_uzytkownika(uzytkownik, opacity, blur):
    """Zapisuje lub aktualizuje ustawienia w arkuszu 'Ustawienia'."""
    try:
        arkusz = get_worksheet("Ustawienia")
        rekordy = arkusz.get_all_records()
        
        wiersz_do_aktualizacji = None
        for i, r in enumerate(rekordy):
            if str(r.get('Uzytkownik', '')) == str(uzytkownik):
                wiersz_do_aktualizacji = i + 2  
                break
                
        if wiersz_do_aktualizacji:
            arkusz.update_cell(wiersz_do_aktualizacji, 2, float(opacity))
            arkusz.update_cell(wiersz_do_aktualizacji, 3, int(blur))
        else:
            arkusz.append_row([str(uzytkownik), float(opacity), int(blur)])
            
    except Exception as e:
        print(f"Błąd zapisu ustawień: {e}")

# --- NOWE FUNKCJE: OBSŁUGA UŻYTKOWNIKÓW (LOGOWANIE) ---

def pobierz_uzytkownikow():
    """Pobiera listę użytkowników z arkusza 'Uzytkownicy' do autoryzacji."""
    try:
        sheet = get_worksheet("Uzytkownicy")
        zapisy = sheet.get_all_records()
        return zapisy
    except Exception as e:
        print(f"Błąd pobierania użytkowników: {e}")
        return []

def dodaj_nowego_uzytkownika(nowy_wiersz):
    """Dodaje nowego użytkownika (Login, PIN, Rola) do arkusza 'Uzytkownicy'."""
    try:
        sheet = get_worksheet("Uzytkownicy")
        # Formatujemy na stringi dla bezpieczeństwa przed wysłaniem
        wiersz_str = [str(x) for x in nowy_wiersz]
        sheet.append_row(wiersz_str)
    except Exception as e:
        print(f"Błąd dodawania użytkownika: {e}")
        raise e
