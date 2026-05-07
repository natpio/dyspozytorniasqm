import streamlit as st
import pandas as pd
from datetime import datetime
import database

def pokaz_tablice():
    # --- NAGŁÓWEK ---
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🏭</span><span class="dashboard-title">Tablica Magazynowa</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Bieżące zadania sprzętowe zaplanowane na dzisiaj.</div>', unsafe_allow_html=True)

    # --- POBRANIE I FILTROWANIE DANYCH ---
    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań w bazie.")
        return

    df = pd.DataFrame(dane)
    dzis = datetime.now().strftime("%Y-%m-%d")
    df_dzis = df[df['Data'] == dzis]

    if df_dzis.empty:
        st.success("Wszystko zrobione! Brak zadań na dzisiaj. Można iść na kawę ☕")
        return

    # Sortowanie po godzinie
    df_dzis['Data_sort'] = pd.to_datetime(df_dzis['Data'], format='%Y-%m-%d', errors='coerce')
    df_dzis = df_dzis.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])

    # Podział zadań na Wydania i Przyjęcia na podstawie 'Typu Akcji'
    df_wydania = df_dzis[df_dzis['Typ Akcji'].str.contains("Dowóz|Odbiór przez klienta", case=False)]
    df_przyjecia = df_dzis[df_dzis['Typ Akcji'].str.contains("Odbiór -|Zwrot przez klienta", case=False)]

    # --- RYSOWANIE TABLICY (2 KOLUMNY) ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 style="color: #e67e22; border-bottom: 3px solid #e67e22; padding-bottom:10px; margin-bottom: 20px;">📤 DO WYDANIA (Szykujemy)</h3>', unsafe_allow_html=True)
        if df_wydania.empty:
            st.info("Brak wydań zaplanowanych na dzisiaj.")
        else:
            for _, row in df_wydania.iterrows():
                # Wywołanie funkcji rysującej kartę w kolorach pomarańczowych
                renderuj_karte(row, "#e67e22", "#fffbeb", "#d97706")

    with col2:
        st.markdown('<h3 style="color: #27ae60; border-bottom: 3px solid #27ae60; padding-bottom:10px; margin-bottom: 20px;">📥 DO PRZYJĘCIA (Wraca)</h3>', unsafe_allow_html=True)
        if df_przyjecia.empty:
            st.info("Brak przyjęć zaplanowanych na dzisiaj.")
        else:
            for _, row in df_przyjecia.iterrows():
                # Wywołanie funkcji rysującej kartę w kolorach zielonych
                renderuj_karte(row, "#27ae60", "#f0fdf4", "#16a34a")

def renderuj_karte(row, kolor_ramki, kolor_tla_pigulki, kolor_tekstu_pigulki):
    """
    Funkcja pomocnicza do rysowania powiększonych kart dla magazynu.
    Zmniejsza przezroczystość, jeśli zadanie ma status 'Zakończone'.
    """
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
