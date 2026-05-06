import streamlit as st
import pandas as pd
from datetime import datetime
import database
import plotly.express as px

def pokaz_dashboard():
    # --- NAGŁÓWEK ---
    st.markdown(
        '<div class="dashboard-header"><span class="dashboard-title-icon">⚙️</span><span class="dashboard-title">Dashboard</span></div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="dashboard-subheader">Przegląd zleceń i operacji na dziś</div>', unsafe_allow_html=True)
    
    # Pobieranie i filtrowanie danych z bazy
    dane = database.pobierz_wszystkie_dane()
    df = pd.DataFrame(dane) if dane else pd.DataFrame()
    
    dzis = datetime.now().strftime("%Y-%m-%d")
    df_dzis = df[df['Data'] == dzis] if not df.empty else pd.DataFrame()
    
    # --- KARTY STATYSTYK (NEOMORFIZM) ---
    wszystkie = len(df_dzis)
    nowe = len(df_dzis[df_dzis['Status'] == 'Nowe']) if not df_dzis.empty else 0
    w_trakcie = len(df_dzis[df_dzis['Status'] == 'W drodze']) if not df_dzis.empty else 0
    zakonczone = len(df_dzis[df_dzis['Status'] == 'Zakończone']) if not df_dzis.empty else 0
    
    cards = [
        {"class": "wszystkie-zlecenia", "title": "Wszystkie zlecenia", "value": wszystkie, "date_icon": "📅", "date_text": f"Dzisiaj ({dzis})", "card_icon": "📅"},
        {"class": "nowe", "title": "Nowe", "value": nowe, "date_icon": "🔥", "date_text": f"Dzisiaj ({dzis})", "card_icon": "🔥"},
        {"class": "w-trakcie", "title": "W trakcie", "value": w_trakcie, "date_icon": "🚜", "date_text": f"Dzisiaj ({dzis})", "card_icon": "🚜"},
        {"class": "zakonczone", "title": "Zakończone", "value": zakonczone, "date_icon": "✅", "date_text": f"Dzisiaj ({dzis})", "card_icon": "✅"}
    ]

    # Renderowanie dynamicznych kart
    cols = st.columns(len(cards))
    for i, card in enumerate(cards):
        with cols[i]:
            card_html = f"""
            <div class="card-container {card['class']}">
                <div class="card-info">
                    <div class="card-title">{card['title']}</div>
                    <div class="card-value">{card['value']}</div>
                    <div class="card-date-pill">
                        <span class="card-date-icon">{card['date_icon']}</span>
                        <span>{card['date_text']}</span>
                    </div>
                </div>
                <div class="card-icon">{card['card_icon']}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    # --- TABELA DZISIEJSZYCH ZLECEŃ ---
    st.markdown(f'<div class="table-header">Zlecenia na dziś ({dzis})</div>', unsafe_allow_html=True)
    
    if not df_dzis.empty:
        # Sortowanie po godzinie
        df_dzis['Data_sort'] = pd.to_datetime(df_dzis['Data'], format='%Y-%m-%d', errors='coerce')
        df_dzis = df_dzis.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        df_dzis = df_dzis.reset_index(drop=True) # Ważne dla poprawnego zebrowania!
        
        # Opcjonalne: uatrakcyjnienie danych ikonami
        status_map = {
            'Nowe': '🔥 Nowe',
            'W drodze': '🚜 W drodze',
            'Zakończone': '✅ Zakończone',
            'Awizacja': '🟠 Awizacja'
        }
        df_dzis['Status'] = df_dzis['Status'].map(lambda x: status_map.get(x, x))
        df_dzis['Lokalizacja'] = df_dzis['Lokalizacja'].apply(lambda x: f"📍 {x}" if pd.notnull(x) and x != "" else x)
        df_dzis['Kontakt'] = df_dzis['Kontakt'].apply(lambda x: f"📞 {x}" if pd.notnull(x) and x != "" else x)
        df_dzis['Klient'] = df_dzis['Klient'].apply(lambda x: f"🏢 {x}" if pd.notnull(x) and x != "" else x)

        # Funkcja Pandas Styler (Zebrowanie + Custom Nagłówki)
        def style_df(styler):
            styler.set_properties(**{'border-radius': '10px'})
            styler.set_table_styles([
                {
                    'selector': 'th', 
                    'props': [
                        ('background-color', '#34495e'), 
                        ('color', '#ffffff'), 
                        ('font-weight', 'bold'), 
                        ('text-transform', 'uppercase'), 
                        ('font-size', '0.75rem'), 
                        ('letter-spacing', '0.05em')
                    ]
                },
                {
                    'selector': 'td', 
                    'props': [
                        ('border-bottom', '1px solid #f1f4f8'), 
                        ('padding', '10px 15px')
                    ]
                },
            ])
            def stripe_rows(row):
                return ['background-color: #f7f9fc' if row.name % 2 != 0 else 'background-color: white' for _ in row]
            
            styler.apply(stripe_rows, axis=1)
            return styler

        styled_df = style_df(df_dzis.style)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # --- WYKRESY KOŁOWE ---
        st.markdown("<br>", unsafe_allow_html=True)
        col_w1, col_w2, col_puste = st.columns([1, 1, 1])
        with col_w1:
            st.markdown('<div class="table-header" style="font-size: 0.9rem;">Zlecenia wg typu</div>', unsafe_allow_html=True)
            fig1 = px.pie(df_dzis, names='Typ Akcji', hole=0.7, template="plotly_white")
            fig1.update_layout(margin=dict(t=10, b=10, l=0, r=0), showlegend=True, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_w2:
            st.markdown('<div class="table-header" style="font-size: 0.9rem;">Zlecenia wg statusu</div>', unsafe_allow_html=True)
            fig2 = px.pie(df_dzis, names='Status', hole=0.7, template="plotly_white")
            fig2.update_layout(margin=dict(t=10, b=10, l=0, r=0), showlegend=True, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)
            
    else:
        st.info("Brak zleceń na dzisiaj. Baza jest pusta.")


def pokaz_formularz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">➕</span><span class="dashboard-title">Nowe Zlecenie</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Wypełnij formularz, aby dodać zadanie do bazy</div>', unsafe_allow_html=True)
    
    with st.form("nowe_zadanie_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data realizacji")
            godzina = st.time_input("Godzina")
            dzial = st.selectbox("Dział", ["Rental", "Realizacja"])
            typ_akcji = st.selectbox("Typ Akcji", ["Dowóz do klienta", "Odbiór od klienta", "Magazyn - Odbiór osobisty przez klienta", "Magazyn - Zwrot osobisty przez klienta"])
            auto = st.selectbox("Auto", ["Brak", "Bus 1 (Renault)", "Bus 2 (Peugeot)"])
        with col2:
            nr_projektu = st.text_input("Nr Projektu (opcjonalnie)")
            klient = st.text_input("Klient")
            lokalizacja = st.text_input("Lokalizacja (adres - puste dla magazynu)")
            kontakt = st.text_input("Kontakt (Imię / Telefon)")

        if st.form_submit_button("Zapisz Zlecenie", type="primary"):
            id_zadania = datetime.now().strftime("%Y%m%d%H%M%S")
            wykonawca = "Łukasz (Magazyn)" if "Magazyn" in typ_akcji else "Dawid"
            status = "Awizacja" if "Magazyn" in typ_akcji else "Nowe"

            nowy_wiersz = [id_zadania, data.strftime("%Y-%m-%d"), godzina.strftime("%H:%M"), dzial, typ_akcji, nr_projektu, klient, lokalizacja, kontakt, auto, status, wykonawca]
            database.dodaj_zadanie(nowy_wiersz)
            st.success(f"Dodano zadanie! Wykonawca: {wykonawca}")
            st.cache_resource.clear()


def pokaz_zarzadzanie():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🛠️</span><span class="dashboard-title">Zarządzanie Bazą</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Tutaj możesz edytować, usuwać i archiwizować wszystkie zadania.</div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        df['Data_sort'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')
        df = df.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
        lista_opcji = df['ID'].astype(str) + " | " + df['Data'].astype(str) + " | " + df['Klient'].astype(str) + " - " + df['Typ Akcji'].astype(str)
        wybor = st.selectbox("Wybierz zadanie do edycji/archiwizacji:", ["-- Wybierz zadanie --"] + lista_opcji.tolist())
        
        if wybor != "-- Wybierz zadanie --":
            wybrane_id = wybor.split(" | ")[0]
            wiersz = df[df['ID'].astype(str) == wybrane_id].iloc[0]
            
            with st.form("formularz_edycji"):
                e_k1, e_k2 = st.columns(2)
                with e_k1:
                    n_data = st.text_input("Data (RRRR-MM-DD)", value=str(wiersz['Data']))
                    n_godzina = st.text_input("Godzina", value=str(wiersz['Godzina']))
                    
                    # Zabezpieczenie listy rozwijanej
                    dzial_options = ["Rental", "Realizacja"]
                    dzial_idx = dzial_options.index(wiersz['Dział']) if wiersz['Dział'] in dzial_options else 0
                    n_dzial = st.selectbox("Dział", dzial_options, index=dzial_idx)
                    
                    n_klient = st.text_input("Klient", value=str(wiersz['Klient']))
                with e_k2:
                    n_status = st.text_input("Status", value=str(wiersz['Status']))
                    n_lokalizacja = st.text_input("Lokalizacja", value=str(wiersz['Lokalizacja']))
                    n_kontakt = st.text_input("Kontakt", value=str(wiersz['Kontakt']))
                    n_wykonawca = st.text_input("Wykonawca", value=str(wiersz['Wykonawca']))
                
                if st.form_submit_button("Zapisz Zmiany"):
                    zaktualizowany_wiersz = [wiersz['ID'], n_data, n_godzina, n_dzial, wiersz['Typ Akcji'], wiersz['Nr Projektu'], n_klient, n_lokalizacja, n_kontakt, wiersz['Auto'], n_status, n_wykonawca]
                    database.edytuj_zadanie(wybrane_id, zaktualizowany_wiersz)
                    st.success("Zmiany zapisane!")
                    st.cache_resource.clear()
                    st.rerun()

            c1, c2 = st.columns(2)
            with c1:
                if st.button("📦 Przenieś do Archiwum", type="primary", use_container_width=True):
                    database.archiwizuj_zadanie(wybrane_id)
                    st.success("Zadanie zarchiwizowane!")
                    st.cache_resource.clear()
                    st.rerun()
            with c2:
                if st.button("🗑️ Usuń to zadanie bezpowrotnie", type="secondary", use_container_width=True):
                    database.usun_zadanie(wybrane_id)
                    st.error("Zadanie usunięte!")
                    st.cache_resource.clear()
                    st.rerun()
    else:
        st.info("Brak zadań w bazie.")


def pokaz_archiwum():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📂</span><span class="dashboard-title">Archiwum Zleceń</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Lista wszystkich zarchiwizowanych zadań historycznych.</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Odśwież Archiwum"):
        st.cache_resource.clear()
        st.rerun()
        
    dane_archiwum = database.pobierz_archiwum()
    
    if dane_archiwum:
        df_arch = pd.DataFrame(dane_archiwum)
        if 'Data' in df_arch.columns and 'Godzina' in df_arch.columns:
             df_arch['Data_sort'] = pd.to_datetime(df_arch['Data'], format='%Y-%m-%d', errors='coerce')
             df_arch = df_arch.sort_values(by=['Data_sort', 'Godzina'], ascending=[False, False]).drop(columns=['Data_sort'])
        
        # Ponowne użycie funkcji stylującej dla Archiwum
        def style_df(styler):
            styler.set_properties(**{'border-radius': '10px'})
            styler.set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#34495e'), ('color', '#ffffff'), ('font-weight', 'bold'), ('text-transform', 'uppercase'), ('font-size', '0.75rem'), ('letter-spacing', '0.05em')]},
                {'selector': 'td', 'props': [('border-bottom', '1px solid #f1f4f8'), ('padding', '10px 15px')]},
            ])
            def stripe_rows(row):
                return ['background-color: #f7f9fc' if row.name % 2 != 0 else 'background-color: white' for _ in row]
            styler.apply(stripe_rows, axis=1)
            return styler
        
        df_arch = df_arch.reset_index(drop=True)
        styled_df = style_df(df_arch.style)
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("Archiwum jest obecnie puste.")


def pokaz_magazyn():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🏭</span><span class="dashboard-title">Panel Magazynu</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Lista sprzętu do przygotowania (wydania) i rozładunku (przyjęcia) na wybrany dzień.</div>', unsafe_allow_html=True)

    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań w bazie.")
        return

    df = pd.DataFrame(dane)
    
    # Wybór daty - domyślnie dzisiaj, ale magazyn może sprawdzić co jest na jutro!
    wybrana_data = st.date_input("Wybierz dzień do analizy:", datetime.now().date())
    df_dzien = df[df['Data'] == wybrana_data.strftime("%Y-%m-%d")]

    if df_dzien.empty:
        st.success(f"Wolne! Brak zaplanowanych ruchów magazynowych na dzień {wybrana_data}.")
        return

    # Sortowanie zadań od najwcześniejszych
    df_dzien['Data_sort'] = pd.to_datetime(df_dzien['Data'], format='%Y-%m-%d', errors='coerce')
    df_dzien = df_dzien.sort_values(by=['Godzina']).drop(columns=['Data_sort'])

    # Podział logiki na Wydania i Przyjęcia
    wydania_typy = ["Dowóz do klienta", "Magazyn - Odbiór osobisty przez klienta"]
    przyjecia_typy = ["Odbiór od klienta", "Magazyn - Zwrot osobisty przez klienta"]

    df_wydania = df_dzien[df_dzien['Typ Akcji'].isin(wydania_typy)]
    df_przyjecia = df_dzien[df_dzien['Typ Akcji'].isin(przyjecia_typy)]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="table-header" style="color: #e67e22;">📤 WYDANIA (Szykujemy do wyjazdu)</div>', unsafe_allow_html=True)
        if df_wydania.empty:
            st.info("Brak wydań tego dnia.")
        else:
            for _, row in df_wydania.iterrows():
                st.markdown(f"""
                <div class="card-container" style="display:block; padding:15px; border-left: 5px solid #e67e22; margin-bottom:15px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <strong style="font-size:1.2rem; color:#e67e22;">⏰ {row['Godzina']}</strong>
                        <span class="card-date-pill" style="background-color:#fffbeb; color:#d97706; font-weight:bold;">
                            🚚 {row['Wykonawca']} ({row['Auto']})
                        </span>
                    </div>
                    <div style="font-size:0.95rem; margin-bottom:5px;"><strong>Projekt:</strong> {row['Nr Projektu']}</div>
                    <div style="font-size:0.95rem; margin-bottom:5px;"><strong>Klient:</strong> {row['Klient']}</div>
                    <div style="font-size:0.85rem; color:#64748b; margin-top:10px; border-top: 1px solid #eee; padding-top: 5px;">
                        <strong>Akcja:</strong> {row['Typ Akcji']} | <strong>Status:</strong> {row['Status']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="table-header" style="color: #27ae60;">📥 PRZYJĘCIA (Wraca na magazyn)</div>', unsafe_allow_html=True)
        if df_przyjecia.empty:
            st.info("Brak przyjęć tego dnia.")
        else:
            for _, row in df_przyjecia.iterrows():
                st.markdown(f"""
                <div class="card-container" style="display:block; padding:15px; border-left: 5px solid #27ae60; margin-bottom:15px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <strong style="font-size:1.2rem; color:#27ae60;">⏰ {row['Godzina']}</strong>
                        <span class="card-date-pill" style="background-color:#f0fdf4; color:#16a34a; font-weight:bold;">
                            🚚 {row['Wykonawca']} ({row['Auto']})
                        </span>
                    </div>
                    <div style="font-size:0.95rem; margin-bottom:5px;"><strong>Projekt:</strong> {row['Nr Projektu']}</div>
                    <div style="font-size:0.95rem; margin-bottom:5px;"><strong>Klient:</strong> {row['Klient']}</div>
                    <div style="font-size:0.85rem; color:#64748b; margin-top:10px; border-top: 1px solid #eee; padding-top: 5px;">
                         <strong>Akcja:</strong> {row['Typ Akcji']} | <strong>Status:</strong> {row['Status']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
