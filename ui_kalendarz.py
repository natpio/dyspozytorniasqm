import streamlit as st
from streamlit_calendar import calendar
import database

def pokaz_kalendarz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🗓️</span><span class="dashboard-title">Harmonogram Pracy</span></div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    events = []
    
    for row in dane:
        events.append({
            "title": f"{row['Godzina']} - {row['Klient']}",
            "start": row['Data'],
            "end": row['Data'],
            "resourceId": row['Wykonawca'],
            "color": "#5d9cec" if row['Status'] == "Nowe" else "#27ae60"
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek"},
        "selectable": True,
    }
    
    calendar(events=events, options=calendar_options)
