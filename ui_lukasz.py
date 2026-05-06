import streamlit as st
import pandas as pd
from datetime import datetime
import database
import plotly.express as px

def pokaz_dashboard():
    # --- NAGŁÓWEK ---
    st.markdown(
        '<div class="dashboard-header"><span class="dashboard-title-icon">📊</span><span class="dashboard-title">Centrum Dowodzenia</span></div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="dashboard-subheader">Bieżący podgląd operacji, statusów i wydajności.</div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    df = pd.DataFrame(dane) if dane else pd.DataFrame()
    
    dzis = datetime.now().strftime("%Y-%m-%d")
    df_dzis = df[df['Data'] == dzis] if not df.empty else pd.DataFrame()
    
    # --- KARTY STATYSTYK ---
    wszystkie = len(df_dzis)
    nowe = len(df_dzis[df_dzis['Status'] == 'Nowe']) if not df_dzis.empty else 0
    w_trakcie = len(df_dzis[df_dzis['Status'] == 'W drodze']) if not df_dzis.empty else 0
    zakonczone = len(df_dzis[df_dzis['Status'] == 'Zakończone']) if not df_dzis.empty else 0
    
    cards = [
        {"class": "wszystkie-zlecenia", "title": "Całkowity Wolumen", "value": wszystkie, "date_icon": "📅", "date_text": f"Na dzień {dzis}", "card_icon": "📦"},
        {"class": "nowe", "title": "Oczekujące (Nowe)", "value": nowe, "date_icon": "🔥", "date_text": "Wymagają akcji", "card_icon": "⏳"},
        {"class": "w-trakcie", "title": "W trakcie", "value": w_trakcie, "date_icon": "🚜", "date_text": "W realizacji", "card_icon": "🚚"},
        {"class": "zakonczone", "title": "Zakończone", "value": zakonczone, "date_icon": "✅", "date_text": "Skończone", "card_icon": "🏆"}
    ]

    cols = st.columns(4)
    for i, card in enumerate(cards):
        with cols[i]:
            st.markdown(f"""
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
            """, unsafe_allow_html=True)

    # --- TABELA INTERAKTYWNA Z FILTROWANIEM ---
    st.markdown('<br>', unsafe_allow_html=True)
    f_col1, f_col2 = st.columns([3, 1])
    with f_col1:
        st.markdown(f'<div class="table-header" style="margin-top:0;">Zlecenia operacyjne ({dzis})</div>', unsafe_allow_html=True)
    
    if not df_dzis.empty:
        with f_col2:
            # PRO FEATURE: Szybkie filtrowanie
            unikalne_statusy = df_dzis['Status'].unique().tolist()
            wybrane_statusy = st.multiselect("Filtruj status:", unikalne_statusy, default=unikalne_statusy, label_visibility="collapsed")
        
        # Aplikowanie filtra
        df_dzis_filtered = df_dzis[df_dzis['Status'].isin(wybrane_statusy)].copy()
        
        df_dzis_filtered['Data_sort'] = pd.to_datetime(df_dzis_filtered['Data'], format='%Y-%m-%d', errors='coerce')
        df_dzis_filtered = df_dzis_filtered.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort']).reset_index(drop=True)
        
        status_map = {'Nowe': '🔥 Nowe', 'W drodze': '🚜 W drodze', 'Zakończone': '✅ Zakończone', 'Awizacja': '🟠 Awizacja'}
        df_dzis_filtered['Status'] = df_dzis_filtered['Status'].map(lambda x: status_map.get(x, x))
        df_dzis_filtered['Lokalizacja'] = df_dzis_filtered['Lokalizacja'].apply(lambda x: f"📍 {x}" if pd.notnull(x) and x != "" else x)
        df_dzis_filtered['Kontakt'] = df_dzis_filtered['Kontakt'].apply(lambda x: f"📞 {x}" if pd.notnull(x) and x != "" else x)
        df_dzis_filtered['Klient'] = df_dzis_filtered['Klient'].apply(lambda x: f"🏢 {x}" if pd.notnull(x) and x != "" else x)

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

        st.dataframe(style_df(df_dzis_filtered.style), use_container_width=True, hide_index=True)
        
        # --- ZAAWANSOWANE WYKRESY KOŁOWE ---
        st.markdown("<br>", unsafe_allow_html=True)
        col_w1, col_w2, col_puste = st.columns([1, 1, 1])
        with col_w1:
            st.markdown('<div class="table-header" style="font-size: 0.9rem;">Rozkład Działów</div>', unsafe_allow_html=True)
            # Dodano inner-text i grubszą obwódkę
            fig1 = px.pie(df_dzis, names='Dział', hole=0.65, template="plotly_white")
            fig1.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
            fig1.update_layout(margin=dict(t=10, b=10, l=0, r=0), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", annotations=[dict(text='Działy', x=0.5, y=0.5, font_size=16, showarrow=False)])
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_w2:
            st.markdown('<div class="table-header" style="font-size: 0.9rem;">Zlecenia wg statusu</div>', unsafe_allow_html=True)
            fig2 = px.pie(df_dzis, names='Status', hole=0.65, template="plotly_white")
            fig2.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
            fig2.update_layout(margin=dict(t=10, b=10, l=0, r=0), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", annotations=[dict(text='Status', x=0.5, y=0.5, font_size=16, showarrow=False)])
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Brak zleceń na dzisiaj. Baza jest pusta.")


def pokaz_formularz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">➕</span><span class="dashboard-title">Nowy Wpis</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Wprowadź precyzyjne dane, aby ułatwić pracę zespołowi.</div>', unsafe_allow_html=True)
    
    with st.form("nowe_zadanie_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Dane Logistyczne**")
            data = st.date_input("Data realizacji")
            godzina = st.time_input("Godzina")
            dzial = st.selectbox("Dział", ["Rental", "Realizacja"])
            typ_akcji = st.selectbox("Typ Akcji", ["Dowóz do klienta", "Odbiór od klienta", "Magazyn - Odbiór osobisty przez klienta", "Magazyn - Zwrot osobisty przez klienta"])
            auto = st.selectbox("Auto", ["Brak", "Bus 1 (Renault)", "Bus 2 (Peugeot)", "Ciężarówka (MAN)"])
        with col2:
            st.markdown("**Dane Kontrahenta**")
            nr_projektu = st.text_input("Nr Projektu (opcjonalnie)")
            klient = st.text_input("Klient (Firma)")
            lokalizacja = st.text_input("Lokalizacja (adres - puste dla magazynu)")
            kontakt = st.text_input("Kontakt (Imię / Telefon)")

        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        if st.form_submit_button("Zapisz w Systemie", type="primary"):
            id_zadania = datetime.now().strftime("%Y%m%d%H%M%S")
            wykonawca = "Łukasz (Magazyn)" if "Magazyn" in typ_akcji else "Dawid"
            status = "Awizacja" if "Magazyn" in typ_akcji else "Nowe"

            nowy_wiersz = [id_zadania, data.strftime("%Y-%m-%d"), godzina.strftime("%H:%M"), dzial, typ_akcji, nr_projektu, klient, lokalizacja, kontakt, auto, status, wykonawca]
            database.dodaj_zadanie(nowy_wiersz)
            
            # PRO FEATURE: Nowoczesny pop-up zamiast zielonego bloku
            st.toast(f"✅ Dodano zadanie! Przypisano do: {wykonawca}", icon="🚀")
            st.cache_resource.clear()


def pokaz_zarzadzanie():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🛠️</span><span class="dashboard-title">Konsola Administracyjna</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Edycja i archiwizacja rekordów bazy danych.</div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        df['Data_sort'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')
        df = df.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
        # PRO FEATURE: Pasek wyszukiwania ułatwiający znalezienie zlecenia
        wyszukiwarka = st.text_input("🔍 Szukaj po nazwie klienta lub projekcie...", "")
        
        lista_opcji = df['ID'].astype(str) + " | " + df['Data'].astype(str) + " | " + df['Klient'].astype(str) + " - " + df['Typ Akcji'].astype(str)
        
        if wyszukiwarka:
            lista_opcji = [opcja for opcja in lista_opcji if wyszukiwarka.lower() in opcja.lower()]
            
        if not lista_opcji:
            st.warning("Brak wyników wyszukiwania.")
            return
            
        wybor = st.selectbox("Wybierz rekord do przetworzenia:", ["-- Wybierz zadanie --"] + lista_opcji)
        
        if wybor != "-- Wybierz zadanie --":
            wybrane_id = wybor.split(" | ")[0]
            wiersz = df[df['ID'].astype(str) == wybrane_id].iloc[0]
            
            st.markdown("<div style='background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #eee; margin-top: 15px;'>", unsafe_allow_html=True)
            with st.form("formularz_edycji"):
                e_k1, e_k2 = st.columns(2)
                with e_k1:
                    n_data = st.text_input("Data (RRRR-MM-DD)", value=str(wiersz['Data']))
                    n_godzina = st.text_input("Godzina", value=str(wiersz['Godzina']))
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
                    st.toast("Zmiany zapisane w bazie!", icon="💾")
                    st.cache_resource.clear()
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📦 Przenieś do Archiwum", type="primary", use_container_width=True):
                    database.archiwizuj_zadanie(wybrane_id)
                    st.cache_resource.clear()
                    st.rerun()
            with c2:
                if st.button("🗑️ Usuń to zadanie bezpowrotnie", type="secondary", use_container_width=True):
                    database.usun_zadanie(wybrane_id)
                    st.cache_resource.clear()
                    st.rerun()
    else:
        st.info("Brak zadań w bazie.")


def pokaz_archiwum():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📂</span><span class="dashboard-title">Archiwum Cyfrowe</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Pełen rejestr zakończonych operacji.</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Odśwież Dane z Chmury"):
        st.cache_resource.clear()
        st.toast("Dane zsynchronizowane!", icon="☁️")
        st.rerun()
        
    dane_archiwum = database.pobierz_archiwum()
    
    if dane_archiwum:
        df_arch = pd.DataFrame(dane_archiwum)
        if 'Data' in df_arch.columns and 'Godzina' in df_arch.columns:
             df_arch['Data_sort'] = pd.to_datetime(df_arch['Data'], format='%Y-%m-%d', errors='coerce')
             df_arch = df_arch.sort_values(by=['Data_sort', 'Godzina'], ascending=[False, False]).drop(columns=['Data_sort'])
        
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
        st.dataframe(style_df(df_arch.style), use_container_width=True, hide_index=True)
    else:
        st.info("Archiwum jest obecnie puste.")


def pokaz_magazyn():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🏭</span><span class="dashboard-title">Logistyka Magazynowa</span></div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań w bazie.")
        return

    df = pd.DataFrame(dane)
    
    col_d1, col_d2 = st.columns([1, 3])
    with col_d1:
        wybrana_data = st.date_input("Analizowany dzień:", datetime.now().date())
    
    df_dzien = df[df['Data'] == wybrana_data.strftime("%Y-%m-%d")]

    if df_dzien.empty:
        st.success(f"Brak zaplanowanych ruchów sprzętowych na dzień {wybrana_data}. Można iść na kawę ☕")
        return

    df_dzien['Data_sort'] = pd.to_datetime(df_dzien['Data'], format='%Y-%m-%d', errors='coerce')
    df_dzien = df_dzien.sort_values(by=['Godzina']).drop(columns=['Data_sort'])

    wydania_typy = ["Dowóz do klienta", "Magazyn - Odbiór osobisty przez klienta"]
    przyjecia_typy = ["Odbiór od klienta", "Magazyn - Zwrot osobisty przez klienta"]

    df_wydania = df_dzien[df_dzien['Typ Akcji'].isin(wydania_typy)]
    df_przyjecia = df_dzien[df_dzien['Typ Akcji'].isin(przyjecia_typy)]

    # PRO FEATURE: Paski postępu dla operacji magazynowych
    st.markdown('<br>', unsafe_allow_html=True)
    prog_col1, prog_col2 = st.columns(2)
    
    with prog_col1:
        if not df_wydania.empty:
            zakonczone_w = len(df_wydania[df_wydania['Status'] == 'Zakończone'])
            total_w = len(df_wydania)
            st.markdown(f"**Postęp Wydań ({zakonczone_w}/{total_w})**")
            st.progress(zakonczone_w / total_w)
            
    with prog_col2:
        if not df_przyjecia.empty:
            zakonczone_p = len(df_przyjecia[df_przyjecia['Status'] == 'Zakończone'])
            total_p = len(df_przyjecia)
            st.markdown(f"**Postęp Przyjęć ({zakonczone_p}/{total_p})**")
            st.progress(zakonczone_p / total_p)

    st.markdown('<br>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="table-header" style="color: #e67e22; border-bottom: 2px solid #e67e22; padding-bottom:5px;">📤 DO WYDANIA (Szykujemy)</div>', unsafe_allow_html=True)
        if df_wydania.empty:
            st.info("Brak wydań tego dnia.")
        else:
            for _, row in df_wydania.iterrows():
                # Wyszarzanie zakończonych zadań
                opacity = "0.5" if row['Status'] == 'Zakończone' else "1"
                st.markdown(f"""
                <div class="card-container" style="opacity: {opacity}; display:block; padding:15px; border-left: 5px solid #e67e22; margin-bottom:15px;">
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
        st.markdown('<div class="table-header" style="color: #27ae60; border-bottom: 2px solid #27ae60; padding-bottom:5px;">📥 DO PRZYJĘCIA (Wraca)</div>', unsafe_allow_html=True)
        if df_przyjecia.empty:
            st.info("Brak przyjęć tego dnia.")
        else:
            for _, row in df_przyjecia.iterrows():
                opacity = "0.5" if row['Status'] == 'Zakończone' else "1"
                st.markdown(f"""
                <div class="card-container" style="opacity: {opacity}; display:block; padding:15px; border-left: 5px solid #27ae60; margin-bottom:15px;">
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
