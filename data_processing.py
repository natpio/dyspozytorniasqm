import pandas as pd
import database
from datetime import datetime

def pobierz_czysty_df():
    """Pobiera wszystkie dane z bazy i zwraca jako DataFrame."""
    dane = database.pobierz_wszystkie_dane()
    if not dane:
        return pd.DataFrame()
    return pd.DataFrame(dane)

def pobierz_dane_na_dzien(wybrana_data=None):
    """
    Zwraca posortowane zadania dla konkretnego dnia.
    Jeśli nie podano daty, domyślnie bierze dzisiejszą.
    """
    df = pobierz_czysty_df()
    if df.empty:
        return df
    
    # Formatowanie daty (obsługuje stringi z formularzy oraz obiekty datetime)
    if wybrana_data is None:
        wybrana_data = datetime.now().strftime("%Y-%m-%d")
    elif hasattr(wybrana_data, 'strftime'):
        wybrana_data = wybrana_data.strftime("%Y-%m-%d")
        
    df_filtr = df[df['Data'] == str(wybrana_data)].copy()
    
    if not df_filtr.empty:
        # Standaryzowane chronologiczne sortowanie
        df_filtr['Data_sort'] = pd.to_datetime(df_filtr['Data'], format='%Y-%m-%d', errors='coerce')
        df_filtr = df_filtr.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
    return df_filtr

def rozdziel_magazyn_wyjazdy(df):
    """Dzieli podany DataFrame na zadania magazynowe i wyjazdy terenowe."""
    if df.empty: 
        return pd.DataFrame(), pd.DataFrame()
    df_magazyn = df[df['Typ Akcji'].str.contains("Magazyn", na=False)].copy()
    df_wyjazdy = df[~df['Typ Akcji'].str.contains("Magazyn", na=False)].copy()
    return df_magazyn, df_wyjazdy

def rozdziel_wydania_przyjecia(df):
    """Dzieli podany DataFrame (np. magazynowy) na wydania sprzętu i powroty."""
    if df.empty: 
        return pd.DataFrame(), pd.DataFrame()
    df_wydania = df[df['Typ Akcji'].str.contains("Dowóz|Odbiór przez klienta", case=False, na=False)].copy()
    df_przyjecia = df[df['Typ Akcji'].str.contains("Odbiór -|Zwrot przez klienta", case=False, na=False)].copy()
    return df_wydania, df_przyjecia
    
def pobierz_zadania_kierowcy(kierowca, wybrana_data=None):
    """Zwraca gotowy pakiet zadań tylko dla wskazanego kierowcy (domyślnie na dziś)."""
    df_dzien = pobierz_dane_na_dzien(wybrana_data)
    if df_dzien.empty: 
        return pd.DataFrame()
    return df_dzien[df_dzien['Wykonawca'] == kierowca].copy()
