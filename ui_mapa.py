import streamlit as st
from streamlit_folium import st_folium
import folium
import database

def pokaz_mape():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📍</span><span class="dashboard-title">Mapa Operacyjna & Routing</span></div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań do wyświetlenia na mapie.")
        return

    # Środek mapy (Poznań)
    m = folium.Map(location=[52.4064, 16.9252], zoom_start=12, tiles="cartodbpositron")

    for row in dane:
        # Przykładowa logika: szukamy współrzędnych w polu 'Lokalizacja' 
        # (W wersji Pro warto dodać geokodowanie adresów przez API)
        loc = [52.40, 16.92] # Domyślne
        
        folium.Marker(
            loc,
            popup=f"Projekt: {row['Nr Projektu']}<br>Status: {row['Status']}",
            tooltip=row['Klient'],
            icon=folium.Icon(color='blue' if row['Status'] != 'Zakończone' else 'green', icon='truck', prefix='fa')
        ).add_to(m)

    st_folium(m, width=None, height=500)
