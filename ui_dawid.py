import streamlit as st
import pandas as pd
import database
from datetime import datetime
import urllib.parse

def pokaz_panel():
    # --- CSS DLA MOBILNEGO WYGLĄDU KIEROWCY ---
    st.markdown("""
    <style>
    .dawid-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #f1f4f8;
        margin-bottom: 15px;
    }
    .dawid-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .dawid-time { font-size: 1.3rem; font-weight: 800; color: #2563eb; }
    .dawid-client { font-size: 1.2rem; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
    .dawid-address { font-size: 0.9rem; color: #64748b; margin-bottom: 12px; }
    
    /* Pigułki statusów */
    .badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
    .badge-nowe { background-color: #fee2e2; color: #dc2626; }
    .badge-akcept { background-color: #e0f2fe; color: #0369a1; }
    .badge-droga { background-color: #fef3c7; color: #d97706; }
    .badge-fin { background-color: #d1fae5; color: #059669; }

    /* Przyciski mobilne */
    div[data-testid="stButton"] button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Pobieramy dynamicznie imię zalogowanego kierowcy z sesji
    obecny_kierowca = st.session_state.get("zalogowany", "Kierowca")

    st.markdown(f'<div class="dashboard-header"><span class="dashboard-title-icon">📱</span><span class="dashboard-title">Panel: {obecny_kierowca}</span></div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań w systemie.")
        return

    df = pd.DataFrame(dane)
    dzis = datetime.now().strftime("%Y-%m-%d")
    
    # Tabela filtruje zadania tylko dla aktualnie zalogowanej osoby
    df_dawid = df[(df['Wykonawca'] == obecny_kierowca) & (df['Data'] == dzis)]

    tab1, tab2 = st.tabs(["📋 Moje zadania", "🕒 Historia (Dziś)"])

    with tab1:
        aktywne = df_dawid[df_dawid['Status'].isin(['Nowe', 'Zaakceptowane', 'W drodze'])]
        
        if aktywne.empty:
            st.success("Wszystkie zadania na dziś zostały wykonane! ✨")
        else:
            for _, row in aktywne.iterrows():
                status = row['Status']
                
                # Zmiana etykiet i kolorów przycisków zależnie od statusu
                if status == 'Nowe':
                    status_html = '<span class="badge badge-nowe">Oczekuje</span>'
                    btn_label = "👍 Akceptuj zlecenie"
                    btn_kind = "primary"
                    nowy_status = "Zaakceptowane"
                elif status == 'Zaakceptowane':
                    status_html = '<span class="badge badge-akcept">Zaakceptowane</span>'
                    btn_label = "▶ Rozpocznij trasę"
                    btn_kind = "primary" 
                    nowy_status = "W drodze"
                else: 
                    status_html = '<span class="badge badge-droga">W realizacji</span>'
                    btn_label = "🏁 Zakończ zadanie"
                    btn_kind = "secondary"
                    nowy_status = "Zakończone"

                st.markdown(f"""
                <div class="dawid-card">
                    <div class="dawid-header">
                        <span class="dawid-time">{row['Godzina']}</span>
                        {status_html}
                    </div>
                    <div class="dawid-client">🏢 {row['Klient']}</div>
                    <div class="dawid-address">📍 {row['Lokalizacja']}</div>
                    <div style="font-size:0.8rem; color:#94a3b8; border-top: 1px solid #f1f5f9; padding-top: 8px; margin-top: 8px;">
                        📦 {row['Typ Akcji']} | <b>PROJ: {row['Nr Projektu']}</b><br>
                        👤 {row['Kontakt']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- INTELIGENTNA NAWIGACJA (Google Maps) ---
                # Budujemy link kierujący od razu do nawigacji w aplikacji map
                adres_url = urllib.parse.quote(row['Lokalizacja'])
                link_nawigacji = f"https://www.google.com/maps/dir/?api=1&destination={adres_url}"
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(btn_label, key=f"btn_{row['ID']}", type=btn_kind, use_container_width=True):
                        database.aktualizuj_status(row['ID'], nowy_status)
                        st.toast(f"Status zmieniony na: {nowy_status}")
                        st.rerun()
                with col2:
                    st.link_button("🧭 Nawiguj", link_nawigacji, use_container_width=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)

    with tab2:
        historia = df_dawid[df_dawid['Status'] == 'Zakończone']
        if historia.empty:
            st.info("Nie zakończyłeś jeszcze żadnego zadania dzisiaj.")
        else:
            for _, row in historia.iterrows():
                st.markdown(f"""
                <div class="dawid-card" style="opacity: 0.6;">
                    <div class="dawid-header">
                        <span class="dawid-time">{row['Godzina']}</span>
                        <span class="badge badge-fin">Ukończono</span>
                    </div>
                    <div class="dawid-client">🏢 {row['Klient']}</div>
                    <div class="dawid-address">📍 {row['Lokalizacja']}</div>
                </div>
                """, unsafe_allow_html=True)
