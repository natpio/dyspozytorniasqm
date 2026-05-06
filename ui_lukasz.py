import streamlit as st
import pandas as pd
from datetime import datetime
import database

def pokaz_formularz():
    st.header("Dodaj nowe zadanie")
    with st.form("nowe_zadanie_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data realizacji")
            godzina = st.time_input("Godzina")
            dzial = st.selectbox("Dział", ["Rental", "Realizacja"])
            typ_akcji = st.selectbox("Typ Akcji", [
                "Dowóz do klienta", "Odbiór od klienta", 
                "Magazyn - Odbiór osobisty przez klienta", "Magazyn - Zwrot osobisty przez klienta"
            ])
            auto = st.selectbox("Auto", ["Brak", "Bus 1 (Renault)", "Bus 2 (Peugeot)"])
        with col2:
            nr_projektu = st.text_input("Nr Projektu (opcjonalnie)")
            klient = st.text_input("Klient")
            lokalizacja = st.text_input("Lokalizacja (adres - zostaw puste dla magazynu)")
            kontakt = st.text_input("Kontakt (Imię / Telefon)")

        if st.form_submit_button("Zapisz Zadanie", type="primary"):
            id_zadania = datetime.now().strftime("%Y%m%d%H%M%S")
            wykonawca = "Łukasz (Magazyn)" if "Magazyn" in typ_akcji else "Dawid"
            status = "Awizacja" if "Magazyn" in typ_akcji else "Nowe"

            nowy_wiersz = [
                id_zadania, data.strftime("%Y-%m-%d"), godzina.strftime("%H:%M"), 
                dzial, typ_akcji, nr_projektu, klient, lokalizacja, 
                kontakt, auto, status, wykonawca
            ]
            
            try:
                database.dodaj_zadanie(nowy_wiersz)
                st.success(f"Zadanie zostało dodane! Wykonawca: {wykonawca}")
                st.cache_resource.clear()
            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")

def pokaz_tabele():
    st.header("Panel Dyspozytora - Podgląd Zadań")
    
    col_odswiez, col_puste = st.columns([1, 4])
    with col_odswiez:
        if st.button("🔄 Odśwież dane"):
            st.cache_resource.clear()
            st.rerun()

    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        
        # Sortowanie po dacie i godzinie
        df['Data_sort'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')
        df = df.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
        # Pobieramy dzisiejszą datę
        dzis = datetime.now().strftime("%Y-%m-%d")
        
        # Tworzymy pod-zakładki dla Łukasza
        tab_dzis, tab_wszystkie = st.tabs(["📅 Dzisiejsze zadania", "🗄️ Pełny harmonogram (Wszystkie)"])
        
        # Funkcja do kolorowania statusów w tabeli Pandas
        def koloruj_statusy(val):
            if val == 'Zakończone': return 'background-color: #198754; color: white;' # Zielony
            elif val == 'W drodze': return 'background-color: #ffc107; color: black;' # Żółty
            elif val == 'Nowe': return 'background-color: #0dcaf0; color: black;' # Błękitny
            elif val == 'Awizacja': return 'background-color: #6c757d; color: white;' # Szary
            return ''

        with tab_dzis:
            df_dzis = df[df['Data'] == dzis]
            
            if not df_dzis.empty:
                # Licznik postępów dla Łukasza
                liczba_zakończonych = len(df_dzis[df_dzis['Status'] == 'Zakończone'])
                liczba_wszystkich = len(df_dzis)
                
                st.metric(label="Wykonane zadania na dziś", value=f"{liczba_zakończonych} / {liczba_wszystkich}")
                
                # Wyświetlamy wystylizowaną tabelę tylko dla dzisiejszych zadań
                st.dataframe(
                    df_dzis.style.map(koloruj_statusy, subset=['Status']), 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Brak zaplanowanych zadań na dzisiejszy dzień.")
                
        with tab_wszystkie:
            # Wyświetlamy wszystkie dane pogrupowane i wystylizowane
            st.dataframe(
                df.style.map(koloruj_statusy, subset=['Status']), 
                use_container_width=True,
                hide_index=True
            )
            
    else:
        st.warning("Brak jakichkolwiek zadań w bazie.")
