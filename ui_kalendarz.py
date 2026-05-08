import streamlit as st
import pandas as pd
import database
import json
from datetime import datetime
import streamlit.components.v1 as components

def pokaz_kalendarz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🗓️</span><span class="dashboard-title">Harmonogram Pracy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Interaktywny podgląd wszystkich zleceń. Kliknij w zadanie, aby zobaczyć szczegóły.</div>', unsafe_allow_html=True)
    
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

                # Zapisujemy pełne dane w extendedProps dla wyskakującego okienka
                events.append({
                    "title": f"{data_obj.strftime('%H:%M')} | {row.get('Wykonawca', 'Brak')} - {row.get('Klient', 'Brak')}",
                    "start": start_iso,
                    "color": kolor,
                    "extendedProps": {
                        "klient": str(row.get('Klient', '')),
                        "projekt": str(row.get('Nr Projektu', '')),
                        "akcja": str(row.get('Typ Akcji', '')),
                        "lokalizacja": str(row.get('Lokalizacja', '')),
                        "kontakt": str(row.get('Kontakt', '')),
                        "auto": str(row.get('Auto', '')),
                        "status": status
                    }
                })
            except Exception:
                pass 

    # Bezpiecznik: ukryte wydarzenie wymuszające rysowanie siatki
    if not events:
        events.append({
            "title": "Brak zadań",
            "start": datetime.now().strftime('%Y-%m-%dT12:00:00'),
            "color": "transparent",
            "textColor": "#94a3b8"
        })

    events_json = json.dumps(events)

    # PEŁNY KOD HTML + PREMIUM CSS (Glassmorphism) + MODAL JS
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet' />
        <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
        <style>
            /* Reset i główne tło iframe */
            body {{
                margin: 0;
                padding: 5px;
                font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: transparent;
            }}
            
            /* Główny kontener kalendarza (Light Mode) */
            #calendar {{
                background-color: #ffffff;
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.04);
                border: 1px solid #f1f5f9;
            }}
            
            /* Nagłówek i Tytuł */
            .fc-toolbar-title {{ 
                font-weight: 900 !important; 
                font-size: 1.6rem !important; 
                color: #0f172a; 
                letter-spacing: -0.5px;
            }}
            
            /* Luksusowe, zaokrąglone przyciski (Pill buttons) */
            .fc-button-primary {{ 
                background-color: #f8fafc !important; 
                color: #475569 !important; 
                border: 1px solid #e2e8f0 !important; 
                border-radius: 12px !important; 
                text-transform: capitalize !important; 
                font-weight: 600 !important;
                box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
                transition: all 0.2s ease !important;
                padding: 8px 16px !important;
            }}
            .fc-button-primary:hover {{ 
                background-color: #f1f5f9 !important; 
                color: #0f172a !important; 
                transform: translateY(-1px); 
            }}
            .fc-button-primary:not(:disabled).fc-button-active, 
            .fc-button-primary:not(:disabled):active {{ 
                background-color: #3b82f6 !important; 
                color: #ffffff !important; 
                border-color: #3b82f6 !important; 
                box-shadow: 0 4px 12px rgba(59,130,246,0.3) !important;
            }}
            
            /* Wygląd pojedynczych zleceń */
            .fc-event {{ 
                border-radius: 6px !important; 
                border: none !important; 
                padding: 5px 8px !important; 
                font-weight: 700 !important; 
                font-size: 0.8rem !important; 
                box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important; 
                cursor: pointer; 
                transition: transform 0.15s ease; 
            }}
            .fc-event:hover {{ transform: scale(1.02); filter: brightness(1.1); }}
            
            /* Złagodzenie siatki dni */
            .fc-theme-standard td, .fc-theme-standard th {{ border-color: #e2e8f0 !important; }}
            .fc-col-header-cell-cushion {{ color: #64748b !important; text-decoration: none !important; font-weight: 700 !important; padding: 10px !important; }}
            .fc-daygrid-day-number {{ color: #475569 !important; text-decoration: none !important; font-weight: 600 !important; }}
            
            /* ========================================= */
            /* WYSKAKUJĄCE OKIENKO (MODAL)               */
            /* ========================================= */
            #eventModal {{
                display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%;
                background-color: rgba(15, 23, 42, 0.7); backdrop-filter: blur(5px);
            }}
            .modal-content {{
                background-color: #ffffff; margin: 10% auto; padding: 25px; border-radius: 15px;
                width: 70%; max-width: 500px; box-shadow: 0 20px 50px rgba(0,0,0,0.3);
                position: relative; animation: slideIn 0.3s ease-out;
            }}
            @keyframes slideIn {{ from {{transform: translateY(-20px); opacity: 0;}} to {{transform: translateY(0); opacity: 1;}} }}
            .close {{ color: #94a3b8; float: right; font-size: 28px; font-weight: bold; cursor: pointer; transition: 0.2s; }}
            .close:hover {{ color: #ef4444; }}
            .modal-header {{ font-size: 1.4rem; font-weight: 900; color: #0f172a; margin-bottom: 15px; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; }}
            .modal-body p {{ margin: 8px 0; font-size: 1.05rem; color: #334155; }}
            .modal-body strong {{ color: #0f172a; }}
            .status-badge {{ display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; background: #e2e8f0; margin-bottom: 10px; color: #0f172a; }}

            /* ========================================= */
            /* 🌙 PREMIUM DARK MODE (Glassmorphism)      */
            /* ========================================= */
            @media (prefers-color-scheme: dark) {{
                #calendar {{ 
                    background: linear-gradient(145deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9)); 
                    backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
                    border: 1px solid rgba(255,255,255,0.08); 
                    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
                }}
                
                .fc-toolbar-title {{ color: #f8fafc !important; }}
                .fc-col-header-cell-cushion, .fc-daygrid-day-number {{ color: #cbd5e1 !important; }}
                
                /* Bardzo subtelna siatka w nocy */
                .fc-theme-standard td, .fc-theme-standard th, .fc-theme-standard .fc-scrollgrid {{ 
                    border-color: rgba(255,255,255,0.06) !important; 
                }}
                
                /* Ciemne przyciski */
                .fc-button-primary {{ background-color: rgba(255,255,255,0.05) !important; color: #cbd5e1 !important; border-color: rgba(255,255,255,0.1) !important; }}
                .fc-button-primary:hover {{ background-color: rgba(255,255,255,0.1) !important; color: #f8fafc !important; }}
                
                /* Widok listy i dzisiejszy dzień */
                .fc-list-day-cushion {{ background-color: rgba(15, 23, 42, 0.8) !important; color: #f8fafc !important; }}
                .fc-list-event:hover td {{ background-color: rgba(255,255,255,0.05) !important; }}
                .fc-day-today {{ background-color: rgba(59, 130, 246, 0.1) !important; }}

                /* Ciemny Modal */
                .modal-content {{ background-color: #1e293b; border: 1px solid #334155; }}
                .modal-header, .modal-body strong {{ color: #f8fafc; border-color: #334155; }}
                .modal-body p {{ color: #cbd5e1; }}
                .status-badge {{ background: rgba(255,255,255,0.1); color: #f8fafc; }}
            }}
        </style>
    </head>
    <body>
        <div id='calendar'></div>
        
        <div id="eventModal">
          <div class="modal-content">
            <span class="close" id="closeModal">&times;</span>
            <div class="modal-header" id="modalTitle">Szczegóły Zlecenia</div>
            <div id="modalStatus" class="status-badge">Status</div>
            <div class="modal-body">
                <p><strong>Projekt:</strong> <span id="mProj"></span></p>
                <p><strong>Akcja:</strong> <span id="mAkcja"></span></p>
                <p><strong>Lokalizacja:</strong> <span id="mAdres"></span></p>
                <p><strong>Kontakt:</strong> <span id="mKontakt"></span></p>
                <p><strong>Pojazd:</strong> <span id="mAuto"></span></p>
            </div>
          </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var calendarEl = document.getElementById('calendar');
                var modal = document.getElementById("eventModal");
                var span = document.getElementById("closeModal");

                var calendar = new FullCalendar.Calendar(calendarEl, {{
                    initialView: 'dayGridMonth',
                    height: 750,
                    contentHeight: 'auto',
                    firstDay: 1, /* Tydzień zaczyna się od poniedziałku */
                    headerToolbar: {{
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,listWeek'
                    }},
                    events: {events_json},
                    
                    // WYWOŁANIE OKIENKA PO KLIKNIĘCIU W WYDARZENIE
                    eventClick: function(info) {{
                        var props = info.event.extendedProps;
                        
                        // Podmiana tekstów w oknie modalnym
                        document.getElementById('modalTitle').innerText = "🏢 " + props.klient;
                        document.getElementById('modalStatus').innerText = "🚦 " + props.status;
                        document.getElementById('mProj').innerText = props.projekt || "Brak";
                        document.getElementById('mAkcja').innerText = props.akcja;
                        document.getElementById('mAdres').innerText = props.lokalizacja || "Magazyn";
                        document.getElementById('mKontakt').innerText = props.kontakt || "Brak danych";
                        document.getElementById('mAuto').innerText = props.auto || "Nie dotyczy";
                        
                        modal.style.display = "block"; // Pokazanie okna
                    }}
                }});
                calendar.render();

                // Mechanizm zamykania okienka (Krzyżyk lub kliknięcie w tło)
                span.onclick = function() {{ modal.style.display = "none"; }}
                window.onclick = function(event) {{ 
                    if (event.target == modal) {{ 
                        modal.style.display = "none"; 
                    }} 
                }}
            }});
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=800)
