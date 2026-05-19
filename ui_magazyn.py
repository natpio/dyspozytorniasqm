import streamlit as st
import data_processing
import pandas as pd
import json
from datetime import datetime, timedelta
import streamlit.components.v1 as components

def pokaz_tablice():
    # --- NAGŁÓWEK ---
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🏭</span><span class="dashboard-title">Centrum Operacyjne Magazynu</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Bieżące operacje sprzętowe oraz moduł planowania długoterminowego.</div>', unsafe_allow_html=True)

    # --- PODZIAŁ NA WYGODNE ZAKŁADKI DOPASOWANE DO EKRANÓW W MAGAZYNIE ---
    tab_dzis, tab_jutro, tab_kalendarz = st.tabs([
        "🎯 Dzisiejsze zadania", 
        "⏭️ Jutrzejszy plan (Szykowanie)", 
        "🗓️ Widok harmonogramu"
    ])

    with tab_dzis:
        dzis = datetime.now().date()
        renderuj_kanban_dla_daty(dzis, "Brak zaplanowanych zadań na dzisiaj. Można iść na kawę ☕")

    with tab_jutro:
        jutro = datetime.now().date() + timedelta(days=1)
        renderuj_kanban_dla_daty(jutro, "Brak zaplanowanych zadań na jutro. 👌")

    with tab_kalendarz:
        st.markdown('<div style="margin-bottom:15px; color:#94a3b8;">Pełny podgląd nadchodzących awizacji i wydań. Kliknij zadanie, aby zobaczyć szczegóły.</div>', unsafe_allow_html=True)
        renderuj_kalendarz_magazynowy()


def renderuj_kanban_dla_daty(wybrana_data, komunikat_o_braku):
    """Renderuje 2-kolumnową tablicę Kanban dla wskazanej daty."""
    df_dzien = data_processing.pobierz_dane_na_dzien(wybrana_data)

    if df_dzien.empty:
        st.success(komunikat_o_braku)
        return

    # Wykorzystujemy centralną logikę biznesową do rozdzielenia wydań i przyjęć
    df_wydania, df_przyjecia = data_processing.rozdziel_wydania_przyjecia(df_dzien)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 style="color: #e67e22; border-bottom: 3px solid #e67e22; padding-bottom:10px; margin-bottom: 20px;">📤 DO WYDANIA (Szykujemy)</h3>', unsafe_allow_html=True)
        if df_wydania.empty:
            st.info("Brak wydań zaplanowanych na ten dzień.")
        else:
            for _, row in df_wydania.iterrows():
                renderuj_karte(row, "#e67e22", "#fffbeb", "#d97706")

    with col2:
        st.markdown('<h3 style="color: #27ae60; border-bottom: 3px solid #27ae60; padding-bottom:10px; margin-bottom: 20px;">📥 DO PRZYJĘCIA (Wraca)</h3>', unsafe_allow_html=True)
        if df_przyjecia.empty:
            st.info("Brak przyjęć zaplanowanych na ten dzień.")
        else:
            for _, row in df_przyjecia.iterrows():
                renderuj_karte(row, "#27ae60", "#f0fdf4", "#16a34a")


def renderuj_karte(row, kolor_ramki, kolor_tla_pigulki, kolor_tekstu_pigulki):
    """Pomocniczy render wielkiej, czytelnej karty magazynowej."""
    opacity = "0.4" if row['Status'] == 'Zakończone' else "1"
    
    html = f"""
    <div class="card-container" style="opacity: {opacity}; display:block; padding:25px; border-left: 10px solid {kolor_ramki}; margin-bottom:20px; background: white; box-shadow: 0 8px 20px rgba(0,0,0,0.08); transition: opacity 0.3s;">
        <div style="display:flex; justify-content:space-between; margin-bottom:15px; align-items: center;">
            <strong style="font-size:1.8rem; color:{kolor_ramki};">⏰ {row['Godzina']}</strong>
            <span style="background-color:{kolor_tla_pigulki}; color:{kolor_tekstu_pigulki}; font-weight:bold; padding: 8px 15px; border-radius: 20px; font-size: 1rem;">
                🚚 {row['Wykonawca']} ({row['Auto']})
            </span>
        </div>
        <div style="font-size:1.15rem; margin-bottom:8px; color: #0f172a;"><strong>Projekt:</strong> {row['Nr Projektu']}</div>
        <div style="font-size:1.15rem; margin-bottom:15px; color: #0f172a;"><strong>Klient:</strong> {row['Klient']}</div>
        <div style="font-size:1rem; color:#64748b; margin-top:15px; border-top: 1px solid #e2e8f0; padding-top: 15px; line-height: 1.6;">
            <strong>📦 Akcja:</strong> {row['Typ Akcji']} <br>
            <strong>📊 Status:</strong> {row['Status']}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def renderuj_kalendarz_magazynowy():
    """Generuje bezpieczny (Tylko do odczytu) kalendarz FullCalendar przefiltrowany pod ruchy magazynowe."""
    import database
    
    dane = database.pobierz_wszystkie_dane()
    events = []
    
    if dane:
        for row in dane:
            try:
                # FILTR BEZPIECZEŃSTWA: Interesują nas wyłącznie ruchy na magazynie lub powiązane z nim awizacje
                typ_akcji = str(row.get('Typ Akcji', ''))
                # Jeśli akcja nie dotyczy magazynu ani bezpośredniego dowozu/odbioru, pomijamy (ukrywamy czysty transport drogowy)
                if not any(x in typ_akcji.lower() for x in ['magazyn', 'dowóz', 'odbiór', 'zwrot']):
                    continue

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
                
                # Przypisanie kolorów pod operacje magazynowe
                kolor = "#e67e22" if "dowóz" in typ_akcji.lower() or "odbior przez klienta" in typ_akcji.lower() else "#27ae60"
                if status == 'Zakończone': 
                    kolor = "#94a3b8" # Szary dla zamkniętych, żeby nie odciągały uwagi

                events.append({
                    "id": str(row.get('ID')),
                    "title": f"🏭 {data_obj.strftime('%H:%M')} | {row.get('Klient', 'Brak')} - {row.get('Nr Projektu', 'Brak')}",
                    "start": start_iso,
                    "color": kolor,
                    "extendedProps": {
                        "klient": str(row.get('Klient', '')),
                        "projekt": str(row.get('Nr Projektu', '')),
                        "akcja": typ_akcji,
                        "lokalizacja": str(row.get('Lokalizacja', '')),
                        "kontakt": str(row.get('Kontakt', '')),
                        "auto": f"{row.get('Wykonawca', 'Brak')} ({row.get('Auto', 'Brak')})",
                        "status": status
                    }
                })
            except Exception:
                pass 

    if not events:
        events.append({
            "id": "dummy",
            "title": "Brak zadań",
            "start": datetime.now().strftime('%Y-%m-%dT12:00:00'),
            "color": "transparent",
            "textColor": "#94a3b8"
        })

    events_json = json.dumps(events)

    # HTML z zablokowaną funkcją edycji (editable: false) - magazyn nie może przypadkowo poprzesuwać planu Łukasza
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet' />
        <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
        <style>
            body {{ margin: 0; padding: 5px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: transparent; }}
            #calendar {{ background-color: #ffffff; border-radius: 15px; padding: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
            .fc-toolbar-title {{ font-weight: 800 !important; font-size: 1.4rem !important; color: #0f172a; }}
            .fc-button-primary {{ background-color: #f1f5f9 !important; color: #475569 !important; border: 1px solid #e2e8f0 !important; border-radius: 10px !important; font-weight: 600 !important; }}
            .fc-button-primary:not(:disabled).fc-button-active {{ background-color: #e67e22 !important; color: #ffffff !important; border-color: #e67e22 !important; }}
            .fc-event {{ border-radius: 6px !important; border: none !important; padding: 4px 8px !important; font-weight: bold; font-size: 0.85rem !important; cursor: pointer; }}
            
            /* Modal style */
            #eventModal {{ display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(15, 23, 42, 0.6); backdrop-filter: blur(3px); }}
            .modal-content {{ background-color: #ffffff; margin: 15% auto; padding: 20px; border-radius: 12px; width: 80%; max-width: 450px; box-shadow: 0 15px 40px rgba(0,0,0,0.2); }}
            .close {{ color: #94a3b8; float: right; font-size: 24px; font-weight: bold; cursor: pointer; }}
            .close:hover {{ color: #ef4444; }}
            .modal-header {{ font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 12px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px; }}
            .modal-body p {{ margin: 6px 0; color: #334155; font-size: 0.95rem; }}
        </style>
    </head>
    <body>
        <div id='calendar'></div>
        
        <div id="eventModal">
          <div class="modal-content">
            <span class="close" id="closeModal">&times;</span>
            <div class="modal-header" id="modalTitle">Szczegóły Awizacji</div>
            <div class="modal-body">
                <p><strong>Operacja:</strong> <span id="mAkcja"></span></p>
                <p><strong>Projekt:</strong> <span id="mProj"></span></p>
                <p><strong>Dostawca / Pojazd:</strong> <span id="mAuto"></span></p>
                <p><strong>Miejsce docelowe:</strong> <span id="mAdres"></span></p>
                <p><strong>Status:</strong> <span id="mStatus"></span></p>
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
                    height: 650,
                    firstDay: 1,
                    editable: false, /* WYŁĄCZONE DRAG & DROP DLA MAGAZYNU (ZAKAZ EDYCJI) */
                    headerToolbar: {{ left: 'prev,next today', center: 'title', right: 'dayGridMonth,listWeek' }},
                    events: {events_json},
                    
                    eventClick: function(info) {{
                        if (info.event.id === "dummy") return;
                        var props = info.event.extendedProps;
                        
                        document.getElementById('modalTitle').innerText = "🏢 " + props.klient;
                        document.getElementById('mAkcja').innerText = props.akcja;
                        document.getElementById('mProj').innerText = props.projekt || "Brak";
                        document.getElementById('mAuto').innerText = props.auto;
                        document.getElementById('mAdres').innerText = props.lokalizacja;
                        document.getElementById('mStatus').innerText = props.status;
                        
                        modal.style.display = "block";
                    }}
                }});
                calendar.render();

                span.onclick = function() {{ modal.style.display = "none"; }}
                window.onclick = function(event) {{ if (event.target == modal) {{ modal.style.display = "none"; }} }}
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=680)
