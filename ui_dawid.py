import streamlit as st
import pandas as pd
import database

def pokaz_panel():
    st.header("Moje zadania na dziś")
    if st.button("🔄 Odśwież moje zadania"):
        st.cache_resource.clear()
        st.rerun()

    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        aktywne_zadania = df[(df['Wykonawca'] == 'Dawid') & (df['Status'].isin(['Nowe', 'W drodze']))]

        if aktywne_zadania.empty:
            st.success("Brak aktywnych wyjazdów! Możesz odpocząć. ☕")
        else:
            for index, row in aktywne_zadania.iterrows():
                ikona = "🔵" if row['Status'] == "Nowe" else "🟡"
                with st.expander(f"{ikona} {row['Godzina']} | {row['Typ Akcji']} - {row['Klient']}", expanded=True):
                    st.write(f"**📍 Adres:** {row['Lokalizacja']}")
                    st.write(f"**📞 Kontakt:** {row['Kontakt']}")
                    st.write(f"**📦 Dział:** {row['Dział']} | **Projekt:** {row['Nr Projektu']}")
                    st.write(f"**Aktualny Status:** {row['Status']}")
                    
                    if row['Status'] == 'Nowe':
                        if st.button("Akceptuję (Ruszam)", key=f"akceptuj_{row['ID']}", type="primary"):
                            database.aktualizuj_status(row['ID'], 'W drodze')
                            st.cache_resource.clear()
                            st.rerun()
                            
                    elif row['Status'] == 'W drodze':
                        if st.button("✅ Zakończ zadanie", key=f"zakoncz_{row['ID']}", type="primary"):
                            database.aktualizuj_status(row['ID'], 'Zakończone')
                            st.cache_resource.clear()
                            st.rerun()
    else:
        st.info("Brak zadań w systemie.")
