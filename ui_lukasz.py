import streamlit as st
import pandas as pd
from datetime import datetime
import database
import plotly.express as px

def pokaz_dashboard():
    st.title("Dashboard")
    st.write("Przegląd zleceń i operacji na dziś")
    
    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań w bazie.")
        return
        
    df = pd.DataFrame(dane)
    dzis = datetime.now().strftime("%Y-%m-%d")
    df_dzis = df[df['Data'] == dzis]
    
    # --- 1. KARTY STATYSTYK (KPI) ---
    wszystkie = len(df_dzis)
    nowe = len(df_dzis[df_dzis['Status'] == 'Nowe'])
    w_trakcie = len(df_dzis[df_dzis['Status'] == 'W drodze'])
    zakonczone = len(df_dzis[df_dzis['Status'] == 'Zakończone'])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Wszystkie zlecenia</div><div class="kpi-value" style="color: #58a6ff;">{wszystkie}</div><div class="kpi-title" style="margin-bottom:0; margin-top:10px;">Dzisiaj</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Nowe</div><div class="kpi-value" style="color: #ff7b72;">{nowe}</div><div class="kpi-title" style="margin-bottom:0; margin-top:10px;">Dzisiaj</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-title">W trakcie</div><div class="kpi-value" style="color: #d2a8ff;">{w_trakcie}</div><div class="kpi-title" style="margin-bottom:0; margin-top:10px;">Dzisiaj</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Zakończone</div><div class="kpi-value" style="color: #3fb950;">{zakonczone}</div><div class="kpi-title" style="margin-bottom:0; margin-top:10px;">Dzisiaj</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # --- 2. TABELA DZISIEJSZYCH ZLECEŃ ---
    st.subheader(f"Zlecenia na dziś ({dzis})")
    
    def koloruj_statusy(val):
        if val == 'Zakończone': return 'background-color: rgba(63, 185, 80, 0.15); color: #3fb950; font-weight: bold;'
        elif val == 'W drodze': return 'background-color: rgba(210, 168, 255, 0.15); color: #d2a8ff; font-weight: bold;'
        elif val == 'Nowe': return 'background-color: rgba(255, 123, 114, 0.15); color: #ff7b72; font-weight: bold;'
        elif val == 'Awizacja': return 'background-color: rgba(139, 148, 158, 0.15); color: #8b949e; font-weight: bold;'
        return ''
        
    if not df_dzis.empty:
        df_dzis['Data_sort'] = pd.to_datetime(df_dzis['Data'], format='%Y-%m-%d', errors='coerce')
        df_dzis = df_dzis.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
        # KULOODPORNE KOLOROWANIE (niezależne od wersji Pandas na serwerze)
        try:
            tabela_style = df_dzis.style.map(koloruj_statusy, subset=['Status'])
        except AttributeError:
            tabela_style = df_dzis.style.applymap(koloruj_statusy, subset=['Status'])
            
        st.dataframe(tabela_style, use_container_width=True, hide_index=True)
    else:
        st.info("Odpoczywamy! Brak zleceń na dzisiaj.")
        
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- 3. WYKRESY KOŁOWE ---
    if not df_dzis.empty:
        col_w1, col_w2, col_puste = st.columns([1, 1, 1])
        with col_w1:
            st.markdown("**Zlecenia wg typu**")
            fig1 = px.pie(df_dzis, names='Typ Akcji', hole=0.7, template="plotly_dark")
            fig1.update_layout(margin=dict(t=10, b=10, l=0, r=0), showlegend=True, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_w2:
            st.markdown("**Zlecenia wg statusu**")
            fig2 = px.pie(df_dzis, names='Status', hole=0.7, template="plotly_dark", color='Status',
                          color_discrete_map={'Zakończone':'#3fb950', 'W drodze':'#d2a8ff', 'Nowe':'#ff7b72', 'Awizacja':'#8b949e'})
            fig2.update_layout(margin=dict(t=10, b=10, l=0, r=0), showlegend=True, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)


def pokaz_formularz():
    st.header("📝 Dodaj nowe zlecenie")
    st.write("Wypełnij formularz, aby dodać zadanie do bazy.")
    with st.form("nowe_zadanie_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data realizacji")
            godzina = st.time_input("Godzina")
            dzial = st.selectbox("Dział", ["Rental", "Realizacja"])
            typ_akcji = st.selectbox("Typ Akcji", ["Dowóz do klienta", "Odbiór od klienta", "Magazyn - Odbiór osobisty przez klienta", "Magazyn - Zwrot osobisty przez klienta"])
            auto = st.selectbox("Auto", ["Brak", "Bus 1 (Renault)", "Bus 2 (Peugeot)"])
        with col2:
            nr_projektu = st.text_input("Nr Projektu (opcjonalnie)")
            klient = st.text_input("Klient")
            lokalizacja = st.text_input("Lokalizacja (adres - puste dla magazynu)")
            kontakt = st.text_input("Kontakt (Imię / Telefon)")

        if st.form_submit_button("Zapisz Zlecenie", type="primary"):
            id_zadania = datetime.now().strftime("%Y%m%d%H%M%S")
            wykonawca = "Łukasz (Magazyn)" if "Magazyn" in typ_akcji else "Dawid"
            status = "Awizacja" if "Magazyn" in typ_akcji else "Nowe"

            nowy_wiersz = [id_zadania, data.strftime("%Y-%m-%d"), godzina.strftime("%H:%M"), dzial, typ_akcji, nr_projektu, klient, lokalizacja, kontakt, auto, status, wykonawca]
            database.dodaj_zadanie(nowy_wiersz)
            st.success(f"Dodano zadanie! Wykonawca: {wykonawca}")
            st.cache_resource.clear()

def pokaz_zarzadzanie():
    st.header("⚙️ Zarządzanie Bazą Danych")
    st.info("Tutaj możesz edytować, usuwać i archiwizować wszystkie zadania w systemie.")
    
    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        df['Data_sort'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')
        df = df.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
        lista_opcji = df['ID'].astype(str) + " | " + df['Data'] + " | " + df['Klient'] + " - " + df['Typ Akcji']
        wybor = st.selectbox("Wybierz zadanie z listy, aby zarządzać:", ["-- Wybierz zadanie --"] + lista_opcji.tolist())
        
        if wybor != "-- Wybierz zadanie --":
            wybrane_id = wybor.split(" | ")[0]
            wiersz = df[df['ID'].astype(str) == wybrane_id].iloc[0]
            
            with st.form("formularz_edycji"):
                e_k1, e_k2 = st.columns(2)
                with e_k1:
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
                    zaktualizowany_wiersz = [wiersz['ID'], n_data, n_godzina, n_dzial, wiersz['Typ Akcji'], wiersz['Nr Projektu'], n_klient, n_lokalizacja, n_kontakt, wiersz['Auto'], n_status, n_wykonawca]
                    database.edytuj_zadanie(wybrane_id, zaktualizowany_wiersz)
                    st.success("Zmiany zapisane!")
                    st.cache_resource.clear()
                    st.rerun()

            c1, c2 = st.columns(2)
            with c1:
                if st.button("📦 Przenieś do Archiwum", type="primary", use_container_width=True):
                    database.archiwizuj_zadanie(wybrane_id)
                    st.cache_resource.clear()
                    st.rerun()
            with c2:
                if st.button("🗑️ Usuń to zadanie bezpowrotnie", type="secondary", use_container_width=True):
                    database.usun_zadanie(wybrane_id)
                    st.cache_resource.clear()
                    st.rerun()
    else:
        st.info("Brak zadań w bazie.")
