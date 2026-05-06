import streamlit as st
import pandas as pd
import database

def pokaz_panel():
    # --- CSS SPECIFICZNY DLA PANELU DAWIDA ---
    st.markdown("""
    <style>
    /* Stylowanie białych, zaokrąglonych kart mobilnych */
    .dawid-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #f1f4f8;
        margin-bottom: -10px; /* Przyciąga guzik do karty */
        position: relative;
        z-index: 1;
    }
    .dawid-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .dawid-time {
        font-size: 1.3rem;
        font-weight: 800;
        color: #2563eb; /* Niebieski jak we wzorcu */
        margin-right: 10px;
    }
    .dawid-type {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
    }
    .dawid-client {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 5px;
    }
    .dawid-address {
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 15px;
    }
    .dawid-project {
        font-size: 0.75rem;
        background-color: #f1f5f9;
        color: #64748b;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 500;
        display: inline-block;
    }
    /* Pigułki statusów */
    .badge-nowe {
        background-color: #eff6ff;
        color: #3b82f6;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-w-trakcie {
        background-color: #fffbeb;
        color: #d97706;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* HACK: Podmiana standardowych guzików Streamlit na mobilne, pełnej szerokości */
    div[data-testid="stButton"] button p {
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    /* Typ PRIMARY = Przycisk "Rozpocznij" (Niebieski) */
    button[kind="primary"] {
        background-color: #1d4ed8 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 0 !important;
        box-shadow: 0 4px 10px rgba(29, 78, 216, 0.2) !important;
        z-index: 2;
    }
    button[kind="primary"]:hover {
        background-color: #1e40af !important;
    }
    /* Typ SECONDARY = Przycisk "Zakończ" (Pomarańczowy) */
    button[kind="secondary"] {
        background-color: #f59e0b !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 0 !important;
        box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2) !important;
        z-index: 2;
    }
    button[kind="secondary"]:hover {
        background-color: #d97706 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- NAGŁÓWEK ---
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📱</span><span class="dashboard-title">Panel Kierowcy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Zadania przypisane do realizacji na dziś</div>', unsafe_allow_html=True)

    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań w systemie.")
        return

    df = pd.DataFrame(dane)
    # Filtrujemy zadania przypisane do Dawida, które nie są jeszcze zakończone
    aktywne_zadania = df[(df['Wykonawca'] == 'Dawid') & (df['Status'].isin(['Nowe', 'W drodze']))]

    if aktywne_zadania.empty:
        st.success("Wszystkie Twoje dzisiejsze zlecenia są zakończone! Możesz odpocząć. ☕")
    else:
        # Zwężamy widok, żeby aplikacja przypominała ekran smartfona
        col_left, col_main, col_right = st.columns([1, 2, 1])
        
        with col_main:
            for index, row in aktywne_zadania.iterrows():
                
                # Ustalanie wyglądu w zależności od statusu zadania
                if row['Status'] == 'Nowe':
                    badge_html = '<span class="badge-nowe">Zaakceptowane</span>'
                    button_label = "▶ Rozpocznij"
                    button_kind = "primary" # Będzie wyłapane przez CSS jako Niebieski
                    nowy_status = 'W drodze'
                else:
                    badge_html = '<span class="badge-w-trakcie">W trakcie</span>'
                    button_label = "✓ Zakończ"
                    button_kind = "secondary" # Będzie wyłapane przez CSS jako Pomarańczowy
                    nowy_status = 'Zakończone'

                # Kod HTML samej wizytówki zadania
                html_card = f"""
                <div class="dawid-card">
                    <div class="dawid-header">
                        <div>
                            <span class="dawid-time">{row['Godzina']}</span>
                            <span class="dawid-type">{row['Typ Akcji']}</span>
                        </div>
                        <div>{badge_html}</div>
                    </div>
                    <div class="dawid-client">{row['Klient']}</div>
                    <div class="dawid-address">📍 {row['Lokalizacja']}</div>
                    <div class="dawid-project">PROJ-{row['Nr Projektu']}</div>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)
                
                # Interaktywny przycisk akcji na dole karty
                if st.button(button_label, key=f"btn_{row['ID']}", type=button_kind, use_container_width=True):
                    database.aktualizuj_status(row['ID'], nowy_status)
                    st.rerun()
                    
                st.markdown("<br>", unsafe_allow_html=True)
