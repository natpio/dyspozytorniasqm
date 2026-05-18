import streamlit as st
import pandas as pd
import database
import data_processing # <--- IMPORT NOWEGO SILNIKA PRZETWARZANIA DANYCH
import urllib.parse

def pokaz_panel():
    # Pobieramy imię zalogowanego kierowcy ze stanu sesji
    kierowca = st.session_state.get("zalogowany", "Nieznany")
    
    # --- CSS DLA MOBILNEGO WYGLĄDU KIEROWCY ---
    st.markdown("""
    <style>
    .dawid-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #f1f4f8;
        margin-bottom: 15px;
    }
    .dawid-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .dawid-time { font-size: 1.3rem; font-weight: 800; color: #2563eb; }
    .dawid-client { font-size: 1.2rem; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
    .dawid-address { font-size: 0.9rem; color: #64748b; margin-bottom: 12px; }
    
    /* Pigułki statusów */
    .badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
    .badge-nowe { background-color: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
    .badge-w-drodze { background-color: #eff6ff; color: #3b82f6; border: 1px solid #bfdbfe; }
    .badge-fin { background-color: #f0fdf4; color: #22c55e; border: 1px solid #bbf7d0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="dashboard-header"><span class="dashboard-title-icon">🚚</span><span class="dashboard-title">Panel Mobilny: {kierowca}</span></div>', unsafe_allow_html=True)

    # --- POBIERANIE ZOPTYMALIZOWANYCH DANYCH DLA KONKRETNEGO KIEROWCY NA DZIŚ ---
    df_dawid = data_processing.pobierz_zadania_kierowcy(kierowca)

    if df_dawid.empty:
        st.success("Brak przypisanych zadań na dzisiaj. Możesz odpocząć! ☕")
        return

    # --- PODZIAŁ NA ZAKŁADKI ---
    tab1, tab2 = st.tabs(["🛣️ Dzisiejsza trasa", "✅ Zakończone"])

    with tab1:
        aktywne = df_dawid[df_dawid['Status'] != 'Zakończone']
        
        if aktywne.empty:
            st.success("Wszystkie zadania na dziś zostały ukończone! 🎉")
        else:
            for _, row in aktywne.iterrows():
                status_klasa = "badge-nowe" if row['Status'] in ['Nowe', 'Zaakceptowane'] else "badge-w-drodze"
                
                st.markdown(f"""
                <div class="dawid-card">
                    <div class="dawid-header">
                        <span class="dawid-time">⏰ {row['Godzina']}</span>
                        <span class="badge {status_klasa}">{row['Status']}</span>
                    </div>
                    <div class="dawid-client">🏢 {row['Klient']}</div>
                    <div class="dawid-address">📍 {row['Lokalizacja']}</div>
                    <div style="font-size: 0.9rem; color: #475569; margin-bottom: 15px;">
                        <strong>Kontakt:</strong> {row['Kontakt']} <br>
                        <strong>Akcja:</strong> {row['Typ Akcji']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Logika przycisków akcji
                nowy_status = "W drodze" if row['Status'] in ['Nowe', 'Zaakceptowane'] else "Zakończone"
                btn_label = "🚀 Rozpocznij Trasę" if nowy_status == "W drodze" else "✅ Oznacz jako Zakończone"
                btn_kind = "primary" if nowy_status == "W drodze" else "secondary"
                
                # Bezpieczny link do nawigacji Google Maps (wymusza wyznaczenie trasy)
                adres_url = urllib.parse.quote(str(row['Lokalizacja']))
                link_nawigacji = f"https://www.google.com/maps/dir/?api=1&destination={adres_url}"
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(btn_label, key=f"btn_{row['ID']}", type=btn_kind, use_container_width=True):
                        database.aktualizuj_status(row['ID'], nowy_status)
                        st.toast(f"Status zmieniony na: {nowy_status}", icon="🔄")
                        st.rerun()
                with col2:
                    st.link_button("🧭 Nawiguj", link_nawigacji, use_container_width=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)

    with tab2:
        historia = df_dawid[df_dawid['Status'] == 'Zakończone']
        
        if historia.empty:
            st.info("Nie zakończyłeś jeszcze żadnego zadania dzisiaj.")
        else:
            for _, row in historia.iterrows():
                st.markdown(f"""
                <div class="dawid-card" style="opacity: 0.6;">
                    <div class="dawid-header">
                        <span class="dawid-time">{row['Godzina']}</span>
                        <span class="badge badge-fin">Ukończono</span>
                    </div>
                    <div class="dawid-client">🏢 {row['Klient']}</div>
                    <div class="dawid-address">📍 {row['Lokalizacja']}</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">
                        Akcja: {row['Typ Akcji']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
