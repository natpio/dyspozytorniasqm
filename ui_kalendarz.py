import streamlit as st
import pandas as pd
import database
import json
from datetime import datetime
import streamlit.components.v1 as components

def pokaz_kalendarz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🗓️</span><span class="dashboard-title">Harmonogram Pracy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Niezawodny silnik kalendarza renderowany natywnie.</div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    events = []
    
    if dane:
        for row in dane:
            try:
                data_surowa = str(row.get('Data', '')).strip()
                godzina_surowa = str(row.get('Godzina', '00:00')).strip()
                
                if not data_surowa or data_surowa.lower() in ['none', 'nan', '']:
                    continue
                    
                datetime_str = f"{data_surowa} {godzina_surowa}"
                data_obj = pd.to_datetime(datetime_str, errors='coerce')
                
                if pd.isna(data_obj):
                    continue
                    
                start_iso = data_obj.strftime('%Y-%m-%dT%H:%M:%S')
                
                status = str(row.get('Status', ''))
                kolor = "#64748b" # Domyślny szary
                if status in ['Nowe', 'Zaakceptowane', 'Awizacja']: kolor = "#e67e22" # Pomarańczowy
                elif status == 'W drodze': kolor = "#3b82f6" # Niebieski
                elif status == 'Zakończone': kolor = "#27ae60" # Zielony

                events.append({
                    "title": f"{data_obj.strftime('%H:%M')} | {row.get('Wykonawca', 'Brak')} - {row.get('Klient', 'Brak')}",
                    "start": start_iso,
                    "color": kolor
                })
            except Exception:
                pass 

    # Bezpiecznik: puste wydarzenie, aby kalendarz narysował siatkę
    if not events:
        events.append({
            "title": "Brak zadań",
            "start": datetime.now().strftime('%Y-%m-%dT12:00:00'),
            "color": "transparent",
            "textColor": "#94a3b8"
        })

    # Konwertujemy nasze dane do czystego JSONa, który przekażemy do JavaScript
    events_json = json.dumps(events)

    # 100% KULOODPORNY KOD HTML/JS WSTRZYKIWANY DO APLIKACJI
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet' />
        <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            #calendar {{
                background-color: #ffffff;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.05);
            }}
            .fc-toolbar-title {{ font-weight: 800 !important; color: #0f172a; }}
            .fc-button-primary {{ background-color: #3b82f6 !important; border-color: #3b82f6 !important; border-radius: 8px !important; text-transform: capitalize !important; }}
            .fc-button-primary:hover {{ background-color: #2563eb !important; }}
            .fc-event {{ cursor: pointer; border-radius: 4px; border: none; padding: 4px; font-weight: bold; font-size: 0.85rem; }}
            
            /* Automatyczny Dark Mode na poziomie HTML! */
            @media (prefers-color-scheme: dark) {{
                #calendar {{ 
                    background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); 
                    border: 1px solid #334155; 
                }}
                .fc-toolbar-title, .fc-col-header-cell-cushion, .fc-daygrid-day-number {{ color: #f8fafc !important; text-decoration: none; }}
                .fc-theme-standard td, .fc-theme-standard th, .fc-theme-standard .fc-scrollgrid {{ border-color: #334155 !important; }}
                .fc-list-day-cushion {{ background-color: #1e293b !important; color: #f8fafc !important; }}
                .fc-list-event:hover td {{ background-color: rgba(255,255,255,0.05) !important; }}
            }}
        </style>
    </head>
    <body>
        <div id='calendar'></div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var calendarEl = document.getElementById('calendar');
                var calendar = new FullCalendar.Calendar(calendarEl, {{
                    initialView: 'dayGridMonth',
                    height: 650, /* Gwarantuje, że kalendarz nie zapadnie się pod ziemię */
                    headerToolbar: {{
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,listWeek'
                    }},
                    events: {events_json}
                }});
                calendar.render();
            }});
        </script>
    </body>
    </html>
    """

    # Wstrzyknięcie kodu HTML bezpośrednio na stronę, wymuszając 700 pikseli wysokości
    components.html(html_code, height=700)
