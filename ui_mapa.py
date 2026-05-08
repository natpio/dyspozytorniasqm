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
            return [coords[0] + random.uniform(-0.01, 0.01), coords[1] + random.uniform(-0.01, 0.01)]
            
    # Jeśli nie rozpoznano miasta, wrzuca pinezkę w losowe okolice bazy w Komornikach
    return [52.3324 + random.uniform(-0.05, 0.05), 16.8058 + random.uniform(-0.05, 0.05)]

def pokaz_mape():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📍</span><span class="dashboard-title">Mapa Operacyjna & Routing</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Bieżący podgląd tras i lokalizacji w oparciu o silnik Google Maps.</div>', unsafe_allow_html=True)

    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań do wyświetlenia na mapie.")
        return

    df = pd.DataFrame(dane)
    
    # Sortowanie chronologiczne dla poprawnego rysowania linii
    df['Sort_DT'] = pd.to_datetime(df['Data'] + ' ' + df['Godzina'], errors='coerce')
    df = df.sort_values('Sort_DT')
    
    # Inicjalizacja czystej mapy (bez domyślnego kafelka)
    m = folium.Map(location=[51.9194, 19.1451], zoom_start=6, tiles=None)

    # MAGIC TRICK: Wstrzyknięcie oryginalnych, dokładnych kafelków drogowych Google Maps
    folium.TileLayer(
        tiles='http://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google Maps',
        name='Google Maps Drogowa',
        overlay=False,
        control=True
    ).add_to(m)

    # Kolory tras dla różnych kierowców
    kolory_tras = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
    kierowcy = df['Wykonawca'].unique()
    mapa_kolorow = {kierowca: kolory_tras[i % len(kolory_tras)] for i, kierowca in enumerate(kierowcy)}

    for kierowca in kierowcy:
        df_kierowca = df[df['Wykonawca'] == kierowca].copy()
        punkty_trasy = []

        for _, row in df_kierowca.iterrows():
            status = str(row.get('Status', ''))
            loc = geokoduj(row.get('Lokalizacja', ''))
            punkty_trasy.append(loc)
            
            # Kolor pinezki zależy od jej statusu
            if status == 'Zakończone':
                kolor_pin = 'green'
                ikona = 'check'
            elif status == 'W drodze':
                kolor_pin = 'blue'
                ikona = 'truck'
            else:
                kolor_pin = 'orange'
                ikona = 'info'
            
            # Tooltip (po najechaniu)
            tooltip_text = f"📅 {row.get('Data', '')} | {row.get('Klient', '')} | Proj: {row.get('Nr Projektu', 'Brak')}"
            
            # Rozbudowana wizytówka (po kliknięciu) z kolorem nagłówka zadanym z koloru trasy
            popup_html = f"""
            <div style="font-family: sans-serif; min-width: 180px;">
                <div style="background: {mapa_kolorow[kierowca]}; color: white; padding: 5px; border-radius: 5px 5px 0 0; font-weight: bold; text-align: center;">
                    {row.get('Data', '')} | {row.get('Godzina', '')}
                </div>
                <div style="padding: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0 0 5px 5px;">
                    <b style="color: #0f172a; font-size: 1.1em;">🏢 {row.get('Klient', '')}</b><br>
                    <hr style="margin: 8px 0; border: 0; border-top: 1px solid #cbd5e1;">
                    <b style="color: #475569;">Akcja:</b> {row.get('Typ Akcji', '')}<br>
                    <b style="color: #475569;">Status:</b> {status}<br>
                    <b style="color: #475569;">Kierowca:</b> {kierowca} ({row.get('Auto', '')})
                </div>
            </div>
            """
            
            folium.Marker(
                location=loc,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=tooltip_text,
                icon=folium.Icon(color=kolor_pin, icon=ikona, prefix='fa')
            ).add_to(m)

        # Rysowanie linii trasy między punktami dla danego kierowcy
        if len(punkty_trasy) > 1:
            folium.PolyLine(
                locations=punkty_trasy,
                color=mapa_kolorow[kierowca],
                weight=4,
                opacity=0.6,
                tooltip=f"Planowana trasa: {kierowca}"
            ).add_to(m)

    # Wstrzyknięcie mapy jako niezależnego komponentu HTML
    components.html(m._repr_html_(), height=650)
