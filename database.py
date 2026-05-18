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

# --- FUNKCJE POMOCNICZE: CZYSZCZENIE BUFORA ---
def czysc_cache_glowny():
    """Wymusza pobranie świeżych danych z bazy przy następnym zapytaniu."""
    pobierz_wszystkie_dane.clear()

def czysc_cache_archiwum():
    pobierz_archiwum.clear()


# --- FUNKCJE: OBSŁUGA ZADAŃ (ODCZYT Z CACHE) ---

@st.cache_data(ttl=30)
def pobierz_wszystkie_dane():
    """Pobiera dane z bufora. Bufor żyje 30 sekund lub do momentu ręcznego wyczyszczenia."""
    try:
        return get_worksheet("Arkusz1").get_all_records()
    except Exception as e:
        print(f"Błąd pobierania danych: {e}")
        return []

@st.cache_data(ttl=30)
def pobierz_archiwum():
    try:
        return get_worksheet("Archiwum").get_all_records()
    except Exception as e:
        print(f"Błąd pobierania archiwum: {e}")
        return []


# --- FUNKCJE: OBSŁUGA ZADAŃ (ZAPIS + INVALIDACJA CACHE) ---

def dodaj_zadanie(wiersz):
    get_worksheet("Arkusz1").append_row(wiersz)
    czysc_cache_glowny() # <--- Pociągamy za spłuczkę po zmianie

def aktualizuj_status(id_zadania, nowy_status):
    arkusz = get_worksheet("Arkusz1")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            arkusz.update_cell(komorka.row, 11, nowy_status)
            czysc_cache_glowny()
    except Exception as e:
        pass

def usun_zadanie(id_zadania):
    arkusz = get_worksheet("Arkusz1")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            arkusz.delete_rows(komorka.row)
            czysc_cache_glowny()
    except Exception as e:
        pass

def archiwizuj_zadanie(id_zadania):
    arkusz = get_worksheet("Arkusz1")
    archiwum = get_worksheet("Archiwum")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            wiersz = arkusz.row_values(komorka.row)
            archiwum.append_row(wiersz)
            arkusz.delete_rows(komorka.row)
            czysc_cache_glowny()
            czysc_cache_archiwum()
    except Exception as e:
        pass

def edytuj_zadanie(id_zadania, nowy_wiersz):
    arkusz = get_worksheet("Arkusz1")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            lista_komorek = arkusz.range(f"A{komorka.row}:L{komorka.row}")
            for i, wartosc in enumerate(nowy_wiersz):
                lista_komorek[i].value = str(wartosc)
            arkusz.update_cells(lista_komorek)
            czysc_cache_glowny()
    except Exception as e:
        pass


# --- FUNKCJE: OBSŁUGA USTAWIEŃ UI ---

@st.cache_data(ttl=300) # 5 minut cache, to się rzadko zmienia
def pobierz_ustawienia_uzytkownika(uzytkownik):
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
            
        pobierz_ustawienia_uzytkownika.clear() # Czyścimy cache ustawień po zapisie
            
    except Exception as e:
        print(f"Błąd zapisu ustawień: {e}")


# --- NOWE FUNKCJE: OBSŁUGA UŻYTKOWNIKÓW (LOGOWANIE) ---

@st.cache_data(ttl=300) # 5 minut cache
def pobierz_uzytkownikow():
    try:
        sheet = get_worksheet("Uzytkownicy")
        zapisy = sheet.get_all_records()
        return zapisy
    except Exception as e:
        print(f"Błąd pobierania użytkowników: {e}")
        return []

def dodaj_nowego_uzytkownika(nowy_wiersz):
    try:
        sheet = get_worksheet("Uzytkownicy")
        wiersz_str = [str(x) for x in nowy_wiersz]
        sheet.append_row(wiersz_str)
        pobierz_uzytkownikow.clear() # Czyścimy cache userów po dodaniu
    except Exception as e:
        print(f"Błąd dodawania użytkownika: {e}")
        raise e
