import streamlit as st
import pandas as pd
import folium
import database
import streamlit.components.v1 as components
import random

def geokoduj(adres):
    """
    Prosty system przypisywania współrzędnych.
    W pełnej wersji można tu podpiąć API Google Maps lub OpenStreetMap.
    """
    miasta = {
        "poznań": [52.4064, 16.9252], "warszawa": [52.2297, 21.0122],
        "kraków": [50.0647, 19.9450], "wrocław": [51.1079, 17.0385],
        "gdańsk": [54.3520, 18.6466], "szczecin": [53.4285, 14.5528],
        "lublin": [51.2465, 22.5684], "katowice": [50.2649, 19.0238],
        "łódź": [51.7592, 19.4560], "magazyn": [52.3324, 16.8058] # Komorniki
    }
    
    adres_lower = str(adres).lower() if adres else ""
    
    for miasto, coords in miasta.items():
        if miasto in adres_lower:
            # Delikatny "szum", by pinezki w tym samym mieście nie nakładały się idealnie na siebie
            return [coords[0] + random.uniform(-0.02, 0.02), coords[1] + random.uniform(-0.02, 0.02)]
            
    # Jeśli nie rozpoznano miasta, domyślnie okolice bazy (Komorniki)
    return [52.3324 + random.uniform(-0.1, 0.1), 16.8058 + random.uniform(-0.1, 0.1)]

def pokaz_mape():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📍</span><span class="dashboard-title">Mapa Operacyjna & Routing</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Zlecenia i trasy wyjazdowe.</div>', unsafe_allow_html=True)

    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań do wyświetlenia na mapie.")
        return

    df = pd.DataFrame(dane)
    
    # Inicjalizacja mapy - startujemy z widokiem na Polskę
    m = folium.Map(location=[51.9194, 19.1451], zoom_start=6, tiles="CartoDB positron")

    for _, row in df.iterrows():
        # Kolorowanie pinezek po statusie
        status = str(row.get('Status', ''))
        if status == 'Zakończone':
            kolor = 'green'
            ikona = 'check'
        elif status == 'W drodze':
            kolor = 'blue'
            ikona = 'truck'
        else:
            kolor = 'orange'
            ikona = 'info'
            
        loc = geokoduj(row.get('Lokalizacja', ''))
        
        # Tekst po najechaniu myszką
        tooltip_text = f"Projekt: {row.get('Nr Projektu', 'Brak')} | {row.get('Klient', '')}"
        
        # Tekst po kliknięciu w pinezkę
        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 150px;">
            <b>🏢 {row.get('Klient', '')}</b><br>
            <hr style="margin: 5px 0;">
            <b>Akcja:</b> {row.get('Typ Akcji', '')}<br>
            <b>Status:</b> {status}<br>
            <b>Kierowca:</b> {row.get('Wykonawca', '')} ({row.get('Auto', '')})
        </div>
        """
        
        folium.Marker(
            location=loc,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip_text,
            icon=folium.Icon(color=kolor, icon=ikona, prefix='fa')
        ).add_to(m)

    # WSTRZYKNIĘCIE KULOODPORNEGO HTML (Rozwiązuje problem znikającej mapy)
    components.html(m._repr_html_(), height=650)
