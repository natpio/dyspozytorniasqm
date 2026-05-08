import streamlit as st
import pandas as pd
import database

def pokaz_panel_uzytkownikow():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">👥</span><span class="dashboard-title">Zarządzanie Personelem</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Dodawaj nowe konta kierowców i pracowników magazynu.</div>', unsafe_allow_html=True)

    tab_lista, tab_dodaj = st.tabs(["📋 Lista Użytkowników", "➕ Dodaj Nowe Konto"])

    with tab_dodaj:
        st.markdown("### Utwórz nowe konto dostępu")
        with st.form("dodaj_uzytkownika", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nowy_login = st.text_input("Nazwa użytkownika (Imię)")
                nowa_rola = st.selectbox("Rola (Poziom dostępu)", ["Kierowca", "Magazyn", "Admin"])
            with col2:
                nowy_pin = st.text_input("Kod PIN (Hasło do logowania)", type="password")
                potwierdz_pin = st.text_input("Potwierdź kod PIN", type="password")

            if st.form_submit_button("Utwórz Konto", type="primary"):
                if not nowy_login or not nowy_pin:
                    st.error("Wszystkie pola są wymagane!")
                elif nowy_pin != potwierdz_pin:
                    st.error("Kody PIN nie są identyczne!")
                else:
                    # Tutaj wywołamy nową funkcję z database.py (opisana poniżej)
                    try:
                        database.dodaj_nowego_uzytkownika([nowy_login, nowy_pin, nowa_rola])
                        st.success(f"Konto dla {nowy_login} zostało pomyślnie utworzone!")
                    except Exception as e:
                        st.error(f"Wystąpił błąd podczas dodawania konta: {e}")

    with tab_lista:
        st.markdown("### Aktualni Użytkownicy w systemie")
        try:
            # Wymaga funkcji pobierz_uzytkownikow() w database.py
            lista_uz = database.pobierz_uzytkownikow()
            if lista_uz:
                df_uz = pd.DataFrame(lista_uz, columns=["Login", "PIN", "Rola"])
                # Maskujemy PIN dla bezpieczeństwa
                df_uz['PIN'] = "****"
                st.dataframe(df_uz, use_container_width=True, hide_index=True)
            else:
                st.info("Brak użytkowników w bazie.")
        except Exception:
            st.warning("Zakładka 'Uzytkownicy' nie została jeszcze poprawnie skonfigurowana w Google Sheets.")
