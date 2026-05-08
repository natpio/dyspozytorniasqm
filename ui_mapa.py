import streamlit as st
import pandas as pd
import folium
import database
import streamlit.components.v1 as components
import random

def geokoduj(adres):
    """
    Prosty system przypisywania współrzędnych na podstawie nazwy miasta.
    Dodaje lekki losowy 'szum', aby pinezki w tym samym mieście nie nakładały się na siebie.
    """
    miasta = {
        "poznań": [52.4064, 16.9252], "warszawa": [52.2297, 21.0122],
        "kraków": [50.0647, 19.9450], "wrocław": [51.1079, 17.0385],
        "gdańsk": [54.3520, 18.6466], "szczecin": [53.4285, 14.5528],
        "lublin": [51.2465, 22.5684], "katowice": [50.2649, 19.0238],
        "łódź": [51.7592, 19.4560], "magazyn": [52.3324, 16.8058] # Baza Komorniki
    }
    
    adres_lower = str(adres).lower() if adres else ""
    
    for miasto, coords in miasta.items():
        if miasto in adres_lower:
            return [coords[0] + random.uniform(-0.02, 0.02), coords[1] + random.uniform(-0.02, 0.02)]
            
    # Jeśli nie rozpoznano miasta, wrzuca pinezkę w losowe okolice bazy w Komornikach
    return [52.3324 + random.uniform(-0.1, 0.1), 16.8058 + random.uniform(-0.1, 0.1)]

def pokaz_mape():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📍</span><span class="dashboard-title">Mapa Operacyjna & Routing</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Zlecenia i trasy wyjazdowe z podglądem harmonogramu.</div>', unsafe_allow_html=True)

    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań do wyświetlenia na mapie.")
        return

    df = pd.DataFrame(dane)
    
    # Inicjalizacja mapy - startujemy z centralnym widokiem na Polskę
    m = folium.Map(location=[51.9194, 19.1451], zoom_start=6, tiles="CartoDB positron")

    for _, row in df.iterrows():
        # Kolorowanie pinezek na podstawie statusu
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
        
        # 1. Tekst po najechaniu myszką (Tooltip z DATĄ)
        tooltip_text = f"📅 {row.get('Data', '')} | {row.get('Klient', '')} | Proj: {row.get('Nr Projektu', 'Brak')}"
        
        # 2. Tekst po kliknięciu w pinezkę (Rozbudowana wizytówka z DATĄ)
        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 180px;">
            <div style="background: #3b82f6; color: white; padding: 5px; border-radius: 5px 5px 0 0; font-weight: bold; text-align: center;">
                {row.get('Data', '')} | {row.get('Godzina', '')}
            </div>
            <div style="padding: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0 0 5px 5px;">
                <b style="color: #0f172a; font-size: 1.1em;">🏢 {row.get('Klient', '')}</b><br>
                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #cbd5e1;">
                <b style="color: #475569;">Akcja:</b> {row.get('Typ Akcji', '')}<br>
                <b style="color: #475569;">Status:</b> {status}<br>
                <b style="color: #475569;">Kierowca:</b> {row.get('Wykonawca', '')} ({row.get('Auto', '')})
            </div>
        </div>
        """
        
        folium.Marker(
            location=loc,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip_text,
            icon=folium.Icon(color=kolor, icon=ikona, prefix='fa')
        ).add_to(m)

    # Wstrzyknięcie mapy jako niezależnego komponentu HTML (Omijamy awaryjność streamlit-folium)
    components.html(m._repr_html_(), height=650)
