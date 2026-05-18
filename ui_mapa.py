import streamlit as st
import folium
import streamlit.components.v1 as components
import hashlib
import data_processing

def geokoduj(adres, seed_string=""):
    """
    Geokodowanie ze stabilnym przesunięciem (hashing).
    Dzięki temu pinezki dla tych samych zadań zawsze lądują w tym samym miejscu.
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
            # Deterministic offset: generujemy pseudolosowe, ale stałe wartości
            if seed_string:
                hash_val = int(hashlib.md5(str(seed_string).encode('utf-8')).hexdigest(), 16)
                offset_lat = ((hash_val % 400) / 10000.0) - 0.02
                offset_lon = (((hash_val // 400) % 400) / 10000.0) - 0.02
                return [coords[0] + offset_lat, coords[1] + offset_lon]
            return coords
            
    # Jeśli miasta nie ma na liście, centrujemy na Magazyn SQM
    return [52.3324, 16.8058]

def pokaz_mape():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🗺️</span><span class="dashboard-title">Radar Operacyjny</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Podgląd na żywo dyslokacji floty i statusu zadań w terenie.</div>', unsafe_allow_html=True)

    # --- POBRANIE ZOPTYMALIZOWANYCH DANYCH ---
    df_dzis = data_processing.pobierz_dane_na_dzien()
    
    if df_dzis.empty:
        st.info("Brak zadań w bazie na dzisiaj.")
        return

    # Odfiltrowujemy zadania wewnątrzmagazynowe, interesują nas tylko wyjazdy
    _, df_wyjazdy = data_processing.rozdziel_magazyn_wyjazdy(df_dzis)

    if df_wyjazdy.empty:
        st.info("Brak aktywnych wyjazdów w terenie na dzisiaj.")
        return

    # Inicjalizacja mapy wyśrodkowanej na Polskę, ciemny motyw
    m = folium.Map(location=[52.0693, 19.4803], zoom_start=6, tiles="CartoDB dark_matter")

    # Mapowanie kolorów do statusów
    kolory_statusow = {
        'Nowe': 'red',
        'Zaakceptowane': 'orange',
        'W drodze': 'blue',
        'Zakończone': 'green'
    }

    # Zbieranie punktów do rysowania tras (grupowane po kierowcach)
    trasy_kierowcow = {}

    for _, row in df_wyjazdy.iterrows():
        id_zadania = row.get('ID', '')
        adres = row.get('Lokalizacja', '')
        status = row.get('Status', 'Nowe')
        kierowca = row.get('Wykonawca', 'Nieznany')
        
        # Używamy ID zadania jako stałego seedu, by pinezka stała w miejscu
        loc = geokoduj(adres, seed_string=id_zadania)
        
        kolor_pin = kolory_statusow.get(status, 'gray')
        ikona = 'truck' if status == 'W drodze' else 'info-sign'
        
        # Zapisujemy punkt do wyrysowania trasy dla danego kierowcy
        if kierowca not in trasy_kierowcow:
            trasy_kierowcow[kierowca] = []
        trasy_kierowcow[kierowca].append(loc)

        tooltip_text = f"{kierowca} - {row.get('Klient', '')} ({status})"
        
        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 200px;">
            <div style="background: {kolor_pin}; color: white; padding: 5px; border-radius: 5px 5px 0 0; font-weight: bold; text-align: center;">
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

    # Rysowanie przerywanej linii trasy między punktami dla danego kierowcy
    for k_name, punkty in trasy_kierowcow.items():
        if len(punkty) > 1:
            folium.PolyLine(
                punkty,
                color="white",
                weight=2,
                opacity=0.5,
                dash_array='5, 5'
            ).add_to(m)

    # Wstrzyknięcie zoptymalizowanej mapy do interfejsu Streamlit
    m.get_root().width = "100%"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()
    components.html(iframe, height=620)
