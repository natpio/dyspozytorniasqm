import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import database

# USUNIĘTO @st.fragment - to on blokował renderowanie komponentu JavaScript!
def pokaz_kalendarz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🗓️</span><span class="dashboard-title">Harmonogram Pracy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Interaktywny podgląd wszystkich zleceń.</div>', unsafe_allow_html=True)

    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań w bazie do wyświetlenia w kalendarzu.")
        return

    events = []
    for row in dane:
        try:
            data_surowa = str(row.get('Data', '')).strip()
            godzina_surowa = str(row.get('Godzina', '00:00')).strip()

            if not data_surowa or data_surowa == 'None':
                continue

            # Łączymy datę i godzinę, a Pandas wymusza idealny format (np. z "8:15" zrobi "08:15:00")
            datetime_str = f"{data_surowa} {godzina_surowa}"
            data_obj = pd.to_datetime(datetime_str, errors='coerce')
            
            if pd.isna(data_obj):
                continue # Pomiń, jeśli data jest zupełnie nieczytelna
            
            # Format ISO wymagany przez kalendarz
            start_iso = data_obj.strftime('%Y-%m-%dT%H:%M:%S')

            # Kolorowanie statusów
            status = str(row.get('Status', ''))
            if status in ['Nowe', 'Zaakceptowane', 'Awizacja']:
                kolor = "#e67e22" # Pomarańczowy
            elif status == 'W drodze':
                kolor = "#3b82f6" # Niebieski
            elif status == 'Zakończone':
                kolor = "#27ae60" # Zielony
            else:
                kolor = "#64748b" # Szary

            events.append({
                "title": f"{data_obj.strftime('%H:%M')} | {row.get('Wykonawca', '')} - {row.get('Klient', 'Nieznany')}",
                "start": start_iso,
                "color": kolor,
            })
        except Exception as e:
            continue 

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listWeek"
        },
        "slotMinTime": "06:00:00",
        "slotMaxTime": "22:00:00",
        "navLinks": True, 
    }

    custom_css = """
    .fc { background-color: white; border-radius: 15px; padding: 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.05); font-family: sans-serif; }
    .fc-toolbar-title { font-weight: bold !important; color: #0f172a; }
    .fc-button-primary { background-color: #3b82f6 !important; border-color: #3b82f6 !important; border-radius: 8px !important; text-transform: capitalize !important;}
    .fc-button-primary:hover { background-color: #2563eb !important; }
    .fc-event { border-radius: 4px !important; border: none !important; padding: 3px 5px !important; cursor: pointer; font-size: 0.85rem; font-weight: bold; }
    
    @media (prefers-color-scheme: dark) {
        .fc { background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)) !important; border: 1px solid #334155 !important; }
        .fc-toolbar-title { color: #f8fafc !important; }
        .fc-col-header-cell-cushion, .fc-daygrid-day-number { color: #cbd5e1 !important; text-decoration: none !important; }
        .fc-theme-standard td, .fc-theme-standard th, .fc-theme-standard .fc-scrollgrid { border-color: #334155 !important; }
        .fc-list-day-cushion { background-color: #1e293b !important; color: #f8fafc !important; }
        .fc-list-event:hover td { background-color: rgba(255,255,255,0.05) !important; }
    }
    """

    calendar(events=events, options=calendar_options, custom_css=custom_css, key="harmonogram_glowny")
