import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import database
from datetime import datetime

def pokaz_kalendarz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🗓️</span><span class="dashboard-title">Harmonogram Pracy</span></div>', unsafe_allow_html=True)
    
    # 1. STYLE GLOBALNE DLA KALENDARZA (Omijają błąd parametru custom_css)
    st.markdown("""
    <style>
    .fc { 
        background-color: white; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.05);
        font-family: sans-serif;
    }
    .fc-toolbar-title { font-weight: 800 !important; font-size: 1.3rem !important; color: #0f172a; }
    .fc-button-primary { background-color: #3b82f6 !important; border-color: #3b82f6 !important; border-radius: 8px !important; text-transform: capitalize !important;}
    .fc-button-primary:hover { background-color: #2563eb !important; }
    .fc-event { border-radius: 4px !important; border: none !important; padding: 3px 5px !important; cursor: pointer; font-size: 0.85rem; font-weight: bold; }
    
    /* 🌙 DARK MODE DLA KALENDARZA */
    @media (prefers-color-scheme: dark) {
        .fc { background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important; border: 1px solid #334155 !important; }
        .fc-toolbar-title { color: #f8fafc !important; }
        .fc-col-header-cell-cushion, .fc-daygrid-day-number { color: #cbd5e1 !important; text-decoration: none !important; }
        .fc-theme-standard td, .fc-theme-standard th, .fc-theme-standard .fc-scrollgrid { border-color: #334155 !important; }
        .fc-list-day-cushion { background-color: #1e293b !important; color: #f8fafc !important; }
        .fc-list-event:hover td { background-color: rgba(255,255,255,0.05) !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    dane = database.pobierz_wszystkie_dane()
    events = []
    
    if dane:
        for row in dane:
            try:
                data_surowa = str(row.get('Data', '')).strip()
                godzina_surowa = str(row.get('Godzina', '00:00')).strip()
                
                # Odrzucamy puste daty i błędy z Pandas ('nan')
                if not data_surowa or data_surowa.lower() in ['none', 'nan', '']:
                    continue
                    
                datetime_str = f"{data_surowa} {godzina_surowa}"
                data_obj = pd.to_datetime(datetime_str, errors='coerce')
                
                if pd.isna(data_obj):
                    continue
                    
                start_iso = data_obj.strftime('%Y-%m-%dT%H:%M:%S')
                
                status = str(row.get('Status', ''))
                kolor = "#64748b" # Domyślny szary
                if status in ['Nowe', 'Zaakceptowane', 'Awizacja']: kolor = "#e67e22" # Pomarańcz
                elif status == 'W drodze': kolor = "#3b82f6" # Niebieski
                elif status == 'Zakończone': kolor = "#27ae60" # Zielony

                events.append({
                    "title": f"{data_obj.strftime('%H:%M')} | {row.get('Wykonawca', 'Brak')} - {row.get('Klient', 'Brak')}",
                    "start": start_iso,
                    "color": kolor
                })
            except Exception:
                pass # Ciche pominięcie wadliwego wiersza

    # Zabezpieczenie przed pustą tablicą (wymusza narysowanie siatki)
    if not events:
        events.append({
            "title": "Brak zaplanowanych zadań",
            "start": datetime.now().strftime('%Y-%m-%d'),
            "color": "transparent",
            "textColor": "#94a3b8"
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listWeek"
        }
    }
    
    # 2. BEZPIECZNE WYWOŁANIE (Bez parametru custom_css)
    try:
        calendar(events=events, options=calendar_options, key="kalendarz_v3_safe")
    except Exception as e:
        st.error(f"Awaria komponentu kalendarza. Szczegóły: {e}")

    # 3. KONSOLA DEBUGOWANIA (Na wypadek dalszych problemów)
    with st.expander("🛠️ Tryb Debugowania (Diagnostyka danych)"):
        st.markdown("Poniżej znajduje się czysty kod JSON wysyłany do silnika kalendarza. Jeśli widzisz tu dane, a kalendarz u góry się nie renderuje, oznacza to problem z biblioteką chmurową.")
        st.write(events)
