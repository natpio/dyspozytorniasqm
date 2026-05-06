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
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Wszystkie zlecenia</div><div class="kpi-value">{wszystkie}</div><div class="kpi-title" style="color:#3b82f6;">🗓️ Dzisiaj</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Nowe</div><div class="kpi-value">{nowe}</div><div class="kpi-title" style="color:#ef4444;">🔥 Dzisiaj</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-title">W trakcie</div><div class="kpi-value">{w_trakcie}</div><div class="kpi-title" style="color:#f59e0b;">🚚 Dzisiaj</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Zakończone</div><div class="kpi-value">{zakonczone}</div><div class="kpi-title" style="color:#10b981;">✅ Dzisiaj</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 2. TABELA DZISIEJSZYCH ZLECEŃ ---
    st.subheader(f"Zlecenia na dziś ({dzis})")
    
    def koloruj_statusy(val):
        if val == 'Zakończone': return 'background-color: #d1fae5; color: #059669; font-weight: 600;'
        elif val == 'W drodze': return 'background-color: #fef3c7; color: #d97706; font-weight: 600;'
        elif val == 'Nowe': return 'background-color: #fee2e red; color: #dc2626; font-weight: 600;'
        elif val == 'Awizacja': return 'background-color: #f1f5f9; color: #475569; font-weight: 600;'
        return ''
        
    if not df_dzis.empty:
        df_dzis['Data_sort'] = pd.to_datetime(df_dzis['Data'], format='%Y-%m-%d', errors='coerce')
        df_dzis = df_dzis.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
        try:
            tabela_style = df_dzis.style.map(koloruj_statusy, subset=['Status'])
        except AttributeError:
            tabela_style = df_dzis.style.applymap(koloruj_statusy, subset=['Status'])
            
        st.dataframe(tabela_style, use_container_width=True, hide_index=True)
    else:
        st.info("Brak zleceń na dzisiaj.")

def pokaz_formularz():
    st.header("📝 Dodaj nowe zlecenie")
    with st.form("nowe_zadanie_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data realizacji")
            godzina = st.time_input("Godzina")
            dzial = st.selectbox("Dział", ["Rental", "Realizacja"])
            typ_akcji = st.selectbox("Typ Akcji", ["Dowóz do klienta", "Odbiór od klienta", "Magazyn - Odbiór osobisty przez klienta", "Magazyn - Zwrot osobisty przez klienta"])
            auto = st.selectbox("Auto", ["Brak", "Bus 1 (Renault)", "Bus 2 (Peugeot)"])
        with col2:
            nr_projektu = st.text_input("Nr Projektu")
            klient = st.text_input("Klient")
            lokalizacja = st.text_input("Lokalizacja")
            kontakt = st.text_input("Kontakt")

        if st.form_submit_button("Zapisz Zlecenie", type="primary"):
            id_zadania = datetime.now().strftime("%Y%m%d%H%M%S")
            wykonawca = "Łukasz (Magazyn)" if "Magazyn" in typ_akcji else "Dawid"
            status = "Awizacja" if "Magazyn" in typ_akcji else "Nowe"
            nowy_wiersz = [id_zadania, data.strftime("%Y-%m-%d"), godzina.strftime("%H:%M"), dzial, typ_akcji, nr_projektu, klient, lokalizacja, kontakt, auto, status, wykonawca]
            database.dodaj_zadanie(nowy_wiersz)
            st.success("Zadanie dodane pomyślnie!")
            st.cache_resource.clear()

def pokaz_zarzadzanie():
    st.header("⚙️ Zarządzanie Bazą")
    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        lista_opcji = df['ID'].astype(str) + " | " + df['Data'].astype(str) + " | " + df['Klient'].astype(str)
        wybor = st.selectbox("Wybierz zadanie do edycji/archiwizacji:", ["-- Wybierz zadanie --"] + lista_opcji.tolist())
        
        if wybor != "-- Wybierz zadanie --":
            wybrane_id = wybor.split(" | ")[0]
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📦 Przenieś do Archiwum", use_container_width=True, type="primary"):
                    database.archiwizuj_zadanie(wybrane_id)
                    st.success("Przeniesiono do archiwum!")
                    st.cache_resource.clear()
                    st.rerun()
            with col2:
                if st.button("🗑️ Usuń na zawsze", use_container_width=True):
                    database.usun_zadanie(wybrane_id)
                    st.warning("Usunięto z bazy!")
                    st.cache_resource.clear()
                    st.rerun()
    else:
        st.info("Brak aktywnych zadań.")

def pokaz_archiwum():
    st.header("📦 Archiwum Zleceń")
    st.write("Lista wszystkich zarchiwizowanych zadań.")
    
    if st.button("🔄 Odśwież listę"):
        st.cache_resource.clear()
        st.rerun()
        
    dane_arch = database.pobierz_archiwum()
    if dane_arch:
        df_arch = pd.DataFrame(dane_arch)
        st.dataframe(df_arch, use_container_width=True, hide_index=True)
    else:
        st.info("Archiwum jest puste.")
