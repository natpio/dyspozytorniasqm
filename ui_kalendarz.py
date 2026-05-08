import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import database
from datetime import datetime

def pokaz_kalendarz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🗓️</span><span class="dashboard-title">Harmonogram Pracy</span></div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    events = []
    
    if dane:
        for row in dane:
            try:
                data_surowa = str(row.get('Data', '')).strip()
                godzina_surowa = str(row.get('Godzina', '00:00')).strip()
                
                # Pomijamy puste i błędne wpisy
                if not data_surowa or data_surowa == 'None':
                    continue
                    
                # Bezpieczne parsowanie (wymusza poprawny format czasu)
                datetime_str = f"{data_surowa} {godzina_surowa}"
                data_obj = pd.to_datetime(datetime_str, errors='coerce')
                
                if pd.isna(data_obj):
                    continue
                    
                # Format ISO absolutnie wymagany przez bibliotekę kalendarza
                start_iso = data_obj.strftime('%Y-%m-%dT%H:%M:%S')
                
                status = str(row.get('Status', ''))
                kolor = "#64748b" # Domyślny szary
                if status in ['Nowe', 'Zaakceptowane', 'Awizacja']: kolor = "#e67e22"
                elif status == 'W drodze': kolor = "#3b82f6"
                elif status == 'Zakończone': kolor = "#27ae60"

                events.append({
                    "title": f"{data_obj.strftime('%H:%M')} | {row.get('Wykonawca', '')} - {row.get('Klient', '')}",
                    "start": start_iso,
                    "color": kolor
                })
            except Exception:
                pass # Ignorujemy błędy pojedynczych wierszy, nie przerywamy rysowania

    # WYMUSZENIE RYSOWANIA SIATKI:
    # Jeśli lista jest pusta, wstawiamy jedno ukryte wydarzenie w tle, 
    # żeby JavaScript nie wywalił błędu pustej tablicy.
    if not events:
        events.append({
            "title": "Brak",
            "start": datetime.now().strftime('%Y-%m-%dT12:00:00'),
            "display": "background",
            "color": "transparent"
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        }
    }
    
    # Minimalistyczny CSS, który na 100% się załaduje
    custom_css = """
    .fc { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .fc-toolbar-title { font-weight: bold !important; font-size: 1.2rem !important; }
    .fc-button { background-color: #3b82f6 !important; border: none !important; border-radius: 8px !important; text-transform: capitalize !important; }
    
    @media (prefers-color-scheme: dark) {
        .fc { background-color: #1e293b !important; color: white !important; border: 1px solid #334155 !important; }
        .fc-toolbar-title, .fc-col-header-cell-cushion, .fc-daygrid-day-number { color: white !important; text-decoration: none; }
        .fc-theme-standard td, .fc-theme-standard th { border-color: #334155 !important; }
    }
    """
    
    # Odpalenie kalendarza (zabezpieczone try-except w razie problemów chmury)
    try:
        calendar(events=events, options=calendar_options, custom_css=custom_css, key="kalendarz_v2")
    except Exception as e:
        st.error(f"Błąd komponentu kalendarza. Odśwież stronę.")
