import streamlit as st
import pandas as pd
import database
from datetime import datetime

@st.fragment
def pokaz_panel():
    # --- CSS DLA MOBILNEGO WYGLĄDU DAWIDA (PREMIUM & DARK MODE) ---
    st.markdown("""
    <style>
    /* Karta zadania z efektem szkła i gładkimi przejściami */
    .dawid-card {
        background-color: white !important;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
        transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .dawid-card:active { transform: scale(0.98); } /* Efekt wciśnięcia karty na telefonie */
    
    .dawid-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .dawid-time { font-size: 1.3rem; font-weight: 900; color: #2563eb; }
    .dawid-client { font-size: 1.15rem; font-weight: 800; color: #0f172a; margin-bottom: 4px; }
    .dawid-address { font-size: 0.95rem; color: #64748b; margin-bottom: 12px; font-weight: 500; }
    
    /* Pigułki statusów - styl nowoczesnego SaaS */
    .badge { padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-nowe { background-color: rgba(220, 38, 38, 0.1); color: #dc2626; }
    .badge-akcept { background-color: rgba(3, 105, 161, 0.1); color: #0369a1; }
    .badge-droga { background-color: rgba(217, 119, 6, 0.1); color: #d97706; }
    .badge-fin { background-color: rgba(5, 150, 105, 0.1); color: #059669; }

    /* Przyciski mobilne - grubsze, idealne pod kciuk */
    div[data-testid="stButton"] button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        padding: 12px 0 !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }

    /* 🌙 DARK MODE ADAPTACJA DLA DAWIDA */
    @media (prefers-color-scheme: dark) {
        .dawid-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important;
            border: 1px solid #334155 !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
        }
        .dawid-time { color: #60a5fa !important; }
        .dawid-client { color: #f8fafc !important; }
        .dawid-address { color: #94a3b8 !important; }
        
        /* Neonowe podświetlenia statusów w nocy */
        .badge-nowe { background-color: rgba(239, 68, 68, 0.15); color: #f87171; text-shadow: 0 0 8px rgba(248,113,113,0.3); }
        .badge-akcept { background-color: rgba(56, 189, 248, 0.15); color: #7dd3fc; text-shadow: 0 0 8px rgba(125,211,252,0.3); }
        .badge-droga { background-color: rgba(251, 191, 36, 0.15); color: #fcd34d; text-shadow: 0 0 8px rgba(252,211,77,0.3); }
        .badge-fin { background-color: rgba(16, 185, 129, 0.15); color: #34d399; text-shadow: 0 0 8px rgba(52,211,153,0.3); }
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
            _, col_mid, _ = st.columns([0.05, 0.9, 0.05])
            with col_mid:
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

                    # Zmiana statusu wywoła st.rerun(), ale dzięki @st.fragment 
                    # przeładuje się TYLKO ten panel kierowcy! Zero "migania" ekranu!
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
            _, col_mid_hist, _ = st.columns([0.05, 0.9, 0.05])
            with col_mid_hist:
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
