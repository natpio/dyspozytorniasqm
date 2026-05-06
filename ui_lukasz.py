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
    st.header("Podgląd bazy danych")
    if st.button("Odśwież tabelę"):
        st.cache_resource.clear()
        st.rerun()

    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Brak zadań w bazie.")
