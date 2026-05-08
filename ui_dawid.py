import streamlit as st
import pandas as pd
import database
from datetime import datetime

@st.fragment
def pokaz_panel():
    # --- CSS DLA MOBILNEGO WYGLĄDU DAWIDA (PREMIUM & DARK MODE) ---
    st.markdown("""
    <style>
    /* Karta zadania z efektem szkła */
    .dawid-card {
        background-color: white !important;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
        transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .dawid-card:active { transform: scale(0.98); }
    
    .dawid-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .dawid-time { font-size: 1.3rem; font-weight: 900; color: #2563eb; }
    .dawid-client { font-size: 1.15rem; font-weight: 800; color: #0f172a; margin-bottom: 4px; }
    .dawid-address { font-size: 0.95rem; color: #64748b; margin-bottom: 12px; font-weight: 500; }
    
    /* Pigułki statusów */
    .badge { padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-nowe { background-color: rgba(220, 38, 38, 0.1); color: #dc2626; }
    .badge-akcept { background-color: rgba(3, 105, 161, 0.1); color: #0369a1; }
    .badge-droga { background-color: rgba(217, 119, 6, 0.1); color: #d97706; }
    .badge-fin { background-color: rgba(5, 150, 105, 0.1); color: #059669; }

    /* 🔥 NADPISANIE BRZYDKIEGO CZERWONEGO KOLORU STREAMLIT 🔥 */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 12px 0 !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%) !important;
    }
    
    div[data-testid="stButton"] button[kind="secondary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 12px 0 !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        transform: translateY(-2px);
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
    }

    /* 🌙 DARK MODE ADAPTACJA */
    @media (prefers-color-scheme: dark) {
        .dawid-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
            border: 1px solid #334155 !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
        }
        .dawid-time { color: #60a5fa !important; }
        .dawid-client { color: #f8fafc !important; }
        .dawid-address { color: #94a3b8 !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań przypisanych do Ciebie.")
        return

    df = pd.DataFrame(dane)
    dzis = datetime.now().strftime("%Y-%m-%d")
    df_dawid = df[(df['Wykonawca'] == 'Dawid') & (df['Data'] == dzis)]

    # TRIK RESPONSYWNY: Centralna kolumna wymusza wygląd aplikacji mobilnej na komputerze. 
    # Na prawdziwym telefonie Streamlit zignoruje to i rozciągnie na 100% ekranu.
    _, col_main, _ = st.columns([1, 1.5, 1])

    with col_main:
        st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📱</span><span class="dashboard-title">Panel Kierowcy</span></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📋 Moje zadania", "🕒 Historia (Dziś)"])

        with tab1:
            aktywne = df_dawid[df_dawid['Status'].isin(['Nowe', 'Zaakceptowane', 'W drodze'])]
            
            if aktywne.empty:
                st.success("Wszystkie zadania na dziś zostały wykonane! ✨")
            else:
                for _, row in aktywne.iterrows():
                    # Logika statusu i przycisku
                    if row['Status'] == 'Nowe':
                        status_html = '<span class="badge badge-nowe">Oczekuje</span>'
                        btn_label = "👍 Akceptuj zlecenie"
                        btn_kind = "primary"
                        nowy_status = "Zaakceptowane"
                    elif row['Status'] == 'Zaakceptowane':
                        status_html = '<span class="badge badge-akcept">Zaakceptowane</span>'
                        btn_label = "▶ Rozpocznij trasę"
                        btn_kind = "primary" 
                        nowy_status = "W drodze"
                    else: # W drodze
                        status_html = '<span class="badge badge-droga">W realizacji</span>'
                        btn_label = "🏁 Zakończ zadanie"
                        btn_kind = "secondary"
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
                        <div style="font-size:0.85rem; color:#94a3b8; border-top: 1px solid rgba(148, 163, 184, 0.2); padding-top: 10px; margin-top: 10px;">
                            📦 {row['Typ Akcji']} | <b style="color: #60a5fa;">PROJ: {row['Nr Projektu']}</b><br>
                            👤 {row['Kontakt']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(btn_label, key=f"btn_{row['ID']}", type=btn_kind, use_container_width=True):
                        database.aktualizuj_status(row['ID'], nowy_status)
                        st.toast(f"Status zmieniony na: {nowy_status}", icon="✅")
                        st.rerun()
                        
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
                            <span class="dawid-time" style="color: #64748b;">{row['Godzina']}</span>
                            <span class="badge badge-fin">Ukończono</span>
                        </div>
                        <div class="dawid-client" style="color: #64748b;">{row['Klient']}</div>
                        <div class="dawid-address">📍 {row['Lokalizacja']}</div>
                    </div>
                    """, unsafe_allow_html=True)
