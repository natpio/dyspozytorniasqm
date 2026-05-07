import streamlit as st
import pandas as pd
import database
from datetime import datetime

def pokaz_panel():
    # --- CSS DLA MOBILNEGO WYGLĄDU DAWIDA ---
    st.markdown("""
    <style>
    .dawid-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #f1f4f8;
        margin-bottom: 10px;
    }
    .dawid-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .dawid-time { font-size: 1.2rem; font-weight: 800; color: #2563eb; }
    .dawid-client { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
    .dawid-address { font-size: 0.9rem; color: #64748b; margin-bottom: 12px; }
    
    /* Pigułki statusów */
    .badge { padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
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

    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📱</span><span class="dashboard-title">Panel Kierowcy</span></div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań przypisanych do Ciebie.")
        return

    df = pd.DataFrame(dane)
    dzis = datetime.now().strftime("%Y-%m-%d")
    
    # Filtrowanie zadań Dawida na dziś
    df_dawid = df[(df['Wykonawca'] == 'Dawid') & (df['Data'] == dzis)]

    tab1, tab2 = st.tabs(["📋 Moje zadania", "🕒 Historia (Dziś)"])

    with tab1:
        aktywne = df_dawid[df_dawid['Status'].isin(['Nowe', 'Zaakceptowane', 'W drodze'])]
        
        if aktywne.empty:
            st.success("Wszystkie zadania na dziś zostały wykonane! ✨")
        else:
            # Kontener centrujący dla widoku mobilnego
            _, col_mid, _ = st.columns([0.1, 0.8, 0.1])
            with col_mid:
                for _, row in aktywne.iterrows():
                    # Logika statusu i przycisku
                    if row['Status'] == 'Nowe':
                        status_html = '<span class="badge badge-nowe">Oczekuje</span>'
                        btn_label = "👍 Akceptuj zlecenie"
                        btn_kind = "primary" # Niebieski w app.py
                        nowy_status = "Zaakceptowane"
                    elif row['Status'] == 'Zaakceptowane':
                        status_html = '<span class="badge badge-akcept">Zaakceptowane</span>'
                        btn_label = "▶ Rozpocznij trasę"
                        btn_kind = "primary" 
                        nowy_status = "W drodze"
                    else: # W drodze
                        status_html = '<span class="badge badge-droga">W realizacji</span>'
                        btn_label = "🏁 Zakończ zadanie"
                        btn_kind = "secondary" # Pomarańczowy w app.py
                        nowy_status = "Zakończone"

                    # Karta zadania
                    st.markdown(f"""
                    <div class="dawid-card">
                        <div class="dawid-header">
                            <span class="dawid-time">{row['Godzina']}</span>
                            {status_html}
                        </div>
                        <div class="dawid-client">{row['Klient']}</div>
                        <div class="dawid-address">📍 {row['Lokalizacja']}</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">
                            📦 {row['Typ Akcji']} | <b>PROJ: {row['Nr Projektu']}</b><br>
                            👤 {row['Kontakt']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(btn_label, key=f"btn_{row['ID']}", type=btn_kind, use_container_width=True):
                        database.aktualizuj_status(row['ID'], nowy_status)
                        st.toast(f"Status zmieniony na: {nowy_status}")
                        st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)

    with tab2:
        historia = df_dawid[df_dawid['Status'] == 'Zakończone']
        if historia.empty:
            st.info("Nie zakończyłeś jeszcze żadnego zadania dzisiaj.")
        else:
            for _, row in historia.iterrows():
                st.markdown(f"""
                <div class="dawid-card" style="opacity: 0.7;">
                    <div class="dawid-header">
                        <span class="dawid-time">{row['Godzina']}</span>
                        <span class="badge badge-fin">Ukończono</span>
                    </div>
                    <div class="dawid-client">{row['Klient']}</div>
                    <div class="dawid-address">📍 {row['Lokalizacja']}</div>
                </div>
                """, unsafe_allow_html=True)
