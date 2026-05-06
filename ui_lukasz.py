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
            lokalizacja = st.text_input("Lokalizacja (adres - puste dla magazynu)")
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
            
            database.dodaj_zadanie(nowy_wiersz)
            st.success(f"Dodano zadanie! Wykonawca: {wykonawca}")
            st.cache_resource.clear()

def pokaz_tabele_i_zarzadzanie():
    st.header("Podgląd i Zarządzanie Zadaniami")

    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        df['Data_sort'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')
        df = df.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
        # --- TABELA ---
        def koloruj_statusy(val):
            if val == 'Zakończone': return 'background-color: #198754; color: white;'
            elif val == 'W drodze': return 'background-color: #ffc107; color: black;'
            elif val == 'Nowe': return 'background-color: #0dcaf0; color: black;'
            elif val == 'Awizacja': return 'background-color: #6c757d; color: white;'
            return ''
            
        st.dataframe(df.style.map(koloruj_statusy, subset=['Status']), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("⚙️ Panel Zarządzania Zadaniami (Edycja / Usuwanie / Archiwum)")
        
        # Tworzymy listę wyboru zadań do edycji
        lista_opcji = df['ID'].astype(str) + " | " + df['Data'] + " | " + df['Klient'] + " - " + df['Typ Akcji']
        wybor = st.selectbox("Wybierz zadanie z listy, aby zarządzać:", ["-- Wybierz zadanie --"] + lista_opcji.tolist())
        
        if wybor != "-- Wybierz zadanie --":
            wybrane_id = wybor.split(" | ")[0]
            wiersz = df[df['ID'].astype(str) == wybrane_id].iloc[0]
            
            with st.expander("✏️ Edytuj / Usuń / Archiwizuj to zadanie", expanded=True):
                # Opcje szybkich akcji
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("📦 Przenieś do Archiwum", type="primary", use_container_width=True):
                        database.archiwizuj_zadanie(wybrane_id)
                        st.success("Zadanie przeniesione do Archiwum!")
                        st.cache_resource.clear()
                        st.rerun()
                with c2:
                    if st.button("🗑️ Usuń to zadanie bezpowrotnie", type="secondary", use_container_width=True):
                        database.usun_zadanie(wybrane_id)
                        st.error("Zadanie usunięte!")
                        st.cache_resource.clear()
                        st.rerun()
                
                st.write("lub edytuj dane:")
                # Formularz edycji
                with st.form("formularz_edycji"):
                    e_k1, e_k2 = st.columns(2)
                    with e_k1:
                        # Pola ładujemy jako stringi dla ułatwienia bezpiecznej edycji
                        n_data = st.text_input("Data (RRRR-MM-DD)", value=str(wiersz['Data']))
                        n_godzina = st.text_input("Godzina", value=str(wiersz['Godzina']))
                        n_dzial = st.selectbox("Dział", ["Rental", "Realizacja"], index=["Rental", "Realizacja"].index(wiersz['Dział']))
                        n_klient = st.text_input("Klient", value=str(wiersz['Klient']))
                    with e_k2:
                        n_status = st.text_input("Status", value=str(wiersz['Status']))
                        n_lokalizacja = st.text_input("Lokalizacja", value=str(wiersz['Lokalizacja']))
                        n_kontakt = st.text_input("Kontakt", value=str(wiersz['Kontakt']))
                        n_wykonawca = st.text_input("Wykonawca", value=str(wiersz['Wykonawca']))
                    
                    if st.form_submit_button("Zapisz Zmiany"):
                        zaktualizowany_wiersz = [
                            wiersz['ID'], n_data, n_godzina, n_dzial, wiersz['Typ Akcji'], 
                            wiersz['Nr Projektu'], n_klient, n_lokalizacja, n_kontakt, 
                            wiersz['Auto'], n_status, n_wykonawca
                        ]
                        database.edytuj_zadanie(wybrane_id, zaktualizowany_wiersz)
                        st.success("Zmiany zapisane!")
                        st.cache_resource.clear()
                        st.rerun()
    else:
        st.info("Brak zadań. Tabela jest pusta.")
