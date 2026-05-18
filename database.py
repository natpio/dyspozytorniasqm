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
    gc = get_gspread_client()
    return gc.open("AplikacjaKasprzak").worksheet(nazwa_arkusza)

def czysc_cache_glowny():
    pobierz_wszystkie_dane.clear()

def czysc_cache_archiwum():
    pobierz_archiwum.clear()

# --- FUNKCJE: OBSŁUGA ZADAŃ ---

@st.cache_data(ttl=30)
def pobierz_wszystkie_dane():
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
        return []

def dodaj_zadanie(wiersz):
    get_worksheet("Arkusz1").append_row(wiersz)
    czysc_cache_glowny()

def aktualizuj_status(id_zadania, nowy_status):
    arkusz = get_worksheet("Arkusz1")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            arkusz.update_cell(komorka.row, 11, nowy_status)
            czysc_cache_glowny()
    except Exception as e: pass

def usun_zadanie(id_zadania):
    arkusz = get_worksheet("Arkusz1")
    try:
        komorka = arkusz.find(str(id_zadania))
        if komorka:
            arkusz.delete_rows(komorka.row)
            czysc_cache_glowny()
    except Exception as e: pass

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
    except Exception as e: pass

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
    except Exception as e: pass


# --- TARCZA OCHRONNA: CZYTANIE WEDŁUG KOLUMN, A NIE NAGŁÓWKÓW ---

@st.cache_data(ttl=300)
def pobierz_ustawienia_uzytkownika(uzytkownik):
    """Odczyt bezpośrednio z kolumn. Niestraszne mu zmienione nagłówki, przecinki czy spacje!"""
    try:
        arkusz = get_worksheet("Ustawienia")
        dane = arkusz.get_all_values()
        if not dane or len(dane) < 2: 
            return 0.75, 4
        
        curr_user = str(uzytkownik).strip().lower()
        
        # Przeszukujemy wiersze (pomijając nagłówek)
        for wiersz in dane[1:]:
            if len(wiersz) > 0:
                db_user = str(wiersz[0]).strip().lower()
                if db_user == curr_user:
                    # Zamiana polskich przecinków na kropki (Kolumna B to Opacity, Kolumna C to Blur)
                    try: op_raw = str(wiersz[1]).replace(',', '.').strip()
                    except: op_raw = "0.75"
                    
                    try: bl_raw = str(wiersz[2]).replace(',', '.').strip()
                    except: bl_raw = "4"
                    
                    # Wymuszenie bezpiecznego formatu liczbowego
                    try: op_val = float(op_raw)
                    except: op_val = 0.75
                    
                    try: bl_val = int(float(bl_raw))
                    except: bl_val = 4
                    
                    return op_val, bl_val
    except Exception as e:
        print(f"Błąd odczytu: {e}")
        pass
        
    return 0.75, 4 

def zapisz_ustawienia_uzytkownika(uzytkownik, opacity, blur):
    try:
        arkusz = get_worksheet("Ustawienia")
        dane = arkusz.get_all_values()
        curr_user = str(uzytkownik).strip().lower()
        
        wiersz_do_aktualizacji = None
        for i, wiersz in enumerate(dane):
            if i > 0 and len(wiersz) > 0:
                if str(wiersz[0]).strip().lower() == curr_user:
                    wiersz_do_aktualizacji = i + 1  
                    break
                    
        if wiersz_do_aktualizacji:
            # Używamy ułamków z kropką - gspread sam sobie poradzi z typowaniem do arkusza
            arkusz.update_cell(wiersz_do_aktualizacji, 2, float(opacity))
            arkusz.update_cell(wiersz_do_aktualizacji, 3, int(blur))
        else:
            arkusz.append_row([str(uzytkownik), float(opacity), int(blur)])
            
        pobierz_ustawienia_uzytkownika.clear() 
            
    except Exception as e:
        print(f"Błąd zapisu ustawień: {e}")

# --- FUNKCJE: OBSŁUGA UŻYTKOWNIKÓW ---

@st.cache_data(ttl=300)
def pobierz_uzytkownikow():
    try:
        sheet = get_worksheet("Uzytkownicy")
        return sheet.get_all_records()
    except Exception as e: return []

def dodaj_nowego_uzytkownika(nowy_wiersz):
    try:
        sheet = get_worksheet("Uzytkownicy")
        wiersz_str = [str(x) for x in nowy_wiersz]
        sheet.append_row(wiersz_str)
        pobierz_uzytkownikow.clear()
    except Exception as e: raise e

# --- FUNKCJE: OBSŁUGA SŁOWNIKÓW (DZIELONE FLOTY) ---

@st.cache_data(ttl=300)
def pobierz_slowniki():
    try:
        arkusz = get_worksheet("Slowniki")
        dane = arkusz.get_all_values()
        
        if not dane or len(dane) < 2:
            return {"Auta": ["Brak danych"], "Działy": ["Rental", "Realizacja"]}

        auta, dzialy = [], []
        for wiersz in dane[1:]:
            if len(wiersz) > 0 and wiersz[0].strip(): auta.append(wiersz[0].strip())
            if len(wiersz) > 1 and wiersz[1].strip(): dzialy.append(wiersz[1].strip())
        return {"Auta": auta, "Działy": dzialy}
    except Exception as e:
        return {"Auta": ["Błąd wczytywania"], "Działy": ["Rental", "Realizacja"]}

def czysc_cache_slownikow():
    pobierz_slowniki.clear()
