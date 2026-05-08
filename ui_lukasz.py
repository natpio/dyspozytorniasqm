import streamlit as st
import pandas as pd
from datetime import datetime
import database

# Lista zdefiniowanych typów akcji
TYPY_AKCJI = [
    "Dowóz - Rental",
    "Odbiór - Rental",
    "Dowóz - Realizacja",
    "Odbiór - Realizacja",
    "Magazyn: Odbiór przez klienta - Rental",
    "Magazyn: Zwrot przez klienta - Rental",
    "Magazyn: Odbiór przez klienta - Realizacja",
    "Magazyn: Zwrot przez klienta - Realizacja"
]

def style_df(styler):
    """Funkcja pomocnicza do stylizowania tabel dopasowana do ciemnego motywu"""
    styler.set_properties(**{'border-radius': '10px', 'background-color': 'transparent'})
    styler.set_table_styles([
        {'selector': 'th', 'props': [('background-color', 'rgba(0,0,0,0.2)'), ('color', '#f8fafc'), ('font-weight', 'bold'), ('text-transform', 'uppercase'), ('font-size', '0.75rem'), ('letter-spacing', '0.05em')]},
        {'selector': 'td', 'props': [('border-bottom', '1px solid rgba(255,255,255,0.05)'), ('padding', '10px 15px')]},
    ])
    def stripe_rows(row):
        return ['background-color: transparent' for _ in row]
    styler.apply(stripe_rows, axis=1)
    return styler

@st.fragment
def pokaz_dashboard():
    # --- NAGŁÓWEK ---
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📊</span><span class="dashboard-title">Centrum Dowodzenia</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Bieżący podgląd operacji, statusów i wydajności.</div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    df = pd.DataFrame(dane) if dane else pd.DataFrame()
    dzis = datetime.now().strftime("%Y-%m-%d")
    df_dzis = df[df['Data'] == dzis] if not df.empty else pd.DataFrame()
    
    # --- KARTY STATYSTYK ---
    wszystkie = len(df_dzis)
    nowe = len(df_dzis[df_dzis['Status'].isin(['Nowe', 'Zaakceptowane', 'Awizacja'])]) if not df_dzis.empty else 0
    w_trakcie = len(df_dzis[df_dzis['Status'] == 'W drodze']) if not df_dzis.empty else 0
    zakonczone = len(df_dzis[df_dzis['Status'] == 'Zakończone']) if not df_dzis.empty else 0
    
    cards = [
        {"class": "wszystkie-zlecenia", "title": "Całkowity Wolumen", "value": wszystkie, "date_icon": "📅", "date_text": f"Na dzień {dzis}", "card_icon": "📦"},
        {"class": "nowe", "title": "Oczekujące / Awizacje", "value": nowe, "date_icon": "🔥", "date_text": "Przed realizacją", "card_icon": "⏳"},
        {"class": "w-trakcie", "title": "W trakcie", "value": w_trakcie, "date_icon": "🚜", "date_text": "W realizacji", "card_icon": "🚚"},
        {"class": "zakonczone", "title": "Zakończone", "value": zakonczone, "date_icon": "✅", "date_text": "Skończone", "card_icon": "🏆"}
    ]

    cols = st.columns(4)
    for i, card in enumerate(cards):
        with cols[i]:
            st.markdown(f"""
            <div class="card-container {card['class']}">
                <div class="card-info"><div class="card-title">{card['title']}</div><div class="card-value">{card['value']}</div>
                    <div class="card-date-pill"><span class="card-date-icon">{card['date_icon']}</span><span>{card['date_text']}</span></div>
                </div><div class="card-icon">{card['card_icon']}</div>
            </div>
            """, unsafe_allow_html=True)

    # --- PODZIAŁ NA DWIE TABELE ---
    st.markdown('<br>', unsafe_allow_html=True)
    
    if not df_dzis.empty:
        df_dzis['Data_sort'] = pd.to_datetime(df_dzis['Data'], format='%Y-%m-%d', errors='coerce')
        df_dzis = df_dzis.sort_values(by=['Data_sort', 'Godzina']).drop(columns=['Data_sort'])
        
        status_map = {'Nowe': '🔥 Nowe (Czeka)', 'Zaakceptowane': '👍 Zaakceptowane', 'W drodze': '🚜 W drodze', 'Zakończone': '✅ Zakończone', 'Awizacja': '🟠 Awizacja'}
        df_dzis['Status'] = df_dzis['Status'].map(lambda x: status_map.get(x, x))
        
        # Filtrowanie Magazyn vs Wyjazdy (Transport)
        df_magazyn = df_dzis[df_dzis['Typ Akcji'].str.contains("Magazyn")].copy()
        df_wyjazdy = df_dzis[~df_dzis['Typ Akcji'].str.contains("Magazyn")].copy()

        # 1. TABELA AWIZACJI MAGAZYNOWYCH
        st.markdown(f'<div class="table-header" style="color:#d97706;">🟠 AWIZACJE MAGAZYN: Dowóz / Odbiór - Rental / Realizacja</div>', unsafe_allow_html=True)
        if not df_magazyn.empty:
            df_m_disp = df_magazyn[['Godzina', 'Nr Projektu', 'Klient', 'Typ Akcji', 'Wykonawca', 'Status']].copy()
            df_m_disp['Klient'] = df_m_disp['Klient'].apply(lambda x: f"🏢 {x}")
            df_m_disp = df_m_disp.reset_index(drop=True)
            st.dataframe(style_df(df_m_disp.style), use_container_width=True, hide_index=True)
        else:
            st.info("Brak awizacji magazynowych na dzisiaj.")

        st.markdown('<br>', unsafe_allow_html=True)

        # 2. TABELA ZLECEŃ WYJAZDOWYCH
        st.markdown(f'<div class="table-header" style="color:#3b82f6;">🚚 WYJAZDY: Dowóz / Odbiór u klienta</div>', unsafe_allow_html=True)
        if not df_wyjazdy.empty:
            df_w_disp = df_wyjazdy[['Godzina', 'Lokalizacja', 'Nr Projektu', 'Klient', 'Kontakt', 'Wykonawca', 'Auto', 'Status']].copy()
            df_w_disp['Lokalizacja'] = df_w_disp['Lokalizacja'].apply(lambda x: f"📍 {x}")
            df_w_disp['Kontakt'] = df_w_disp['Kontakt'].apply(lambda x: f"📞 {x}")
            df_w_disp['Klient'] = df_w_disp['Klient'].apply(lambda x: f"🏢 {x}")
            df_w_disp = df_w_disp.reset_index(drop=True)
            st.dataframe(style_df(df_w_disp.style), use_container_width=True, hide_index=True)
        else:
            st.info("Brak wyjazdów transportowych na dzisiaj.")

    else:
        st.info("Brak zleceń na dzisiaj. Baza jest pusta.")

# ==========================================
# ROZDZIELONY FORMULARZ (Wyjazdy i Awizacje)
# ==========================================
@st.fragment
def pokaz_formularz():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">➕</span><span class="dashboard-title">Rejestracja Zadań</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Wybierz odpowiednią zakładkę dla operacji magazynowej lub wyjazdu terenowego.</div>', unsafe_allow_html=True)
    
    # Podział na dwie zakładki
    tab_wyjazd, tab_awizacja = st.tabs(["🚚 Zlecenie Wyjazdu (Dla Kierowcy)", "🏭 Awizacja Magazynowa (Klient u nas)"])

    # --- ZAKŁADKA 1: WYJAZDY ---
    with tab_wyjazd:
        with st.form("form_wyjazd", clear_on_submit=True):
            st.info("💡 Formularz wygeneruje zadanie na panelu mobilnym kierowcy (Dawida).")
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data wyjazdu")
                godzina = st.time_input("Godzina na miejscu")
                dzial = st.selectbox("Dział", ["Rental", "Realizacja"])
                typ_akcji = st.selectbox("Typ zadania", ["Dowóz do klienta", "Odbiór od klienta"])
                auto = st.selectbox("Auto", ["Bus 1 (Renault)", "Bus 2 (Peugeot)", "Ciężarówka (MAN)"])
            with col2:
                nr_projektu = st.text_input("Nr Projektu (opcjonalnie)")
                klient = st.text_input("Klient (Firma) *", placeholder="Wymagane")
                lokalizacja = st.text_input("Lokalizacja (Adres) *", placeholder="Dokładny adres")
                kontakt = st.text_input("Osoba kontaktowa na miejscu i Telefon")

            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 10px 0;'>", unsafe_allow_html=True)
            if st.form_submit_button("Wyślij Zlecenie Wyjazdu", type="primary"):
                if klient and lokalizacja:
                    id_zadania = datetime.now().strftime("%Y%m%d%H%M%S")
                    akcja_format = f"{'Dowóz' if 'Dowóz' in typ_akcji else 'Odbiór'} - {dzial}"
                    # Sztywno przypisujemy Dawida i status Nowe
                    nowy_wiersz = [id_zadania, data.strftime("%Y-%m-%d"), godzina.strftime("%H:%M"), dzial, akcja_format, nr_projektu, klient, lokalizacja, kontakt, auto, "Nowe", "Dawid"]
                    database.dodaj_zadanie(nowy_wiersz)
                    st.toast("✅ Zlecenie wysłane do kierowcy!", icon="🚚")
                else:
                    st.error("Uzupełnij nazwę klienta i adres!")

    # --- ZAKŁADKA 2: AWIZACJE ---
    with tab_awizacja:
        with st.form("form_awizacja", clear_on_submit=True):
            st.warning("🏢 Powiadomienie trafi wyłącznie na tablicę Magazynu. Zlecenie nie pojawi się u kierowcy.")
            col1, col2 = st.columns(2)
            with col1:
                data_awiz = st.date_input("Data przyjazdu klienta", key="d_a")
                godzina_awiz = st.time_input("Szacowana godzina", key="g_a")
                dzial_awiz = st.selectbox("Dział", ["Rental", "Realizacja"], key="dz_a")
                typ_akcji_awiz = st.selectbox("Co się dzieje na magazynie?", ["Klient odbiera sprzęt", "Klient zwraca sprzęt"])
            with col2:
                nr_projektu_awiz = st.text_input("Nr Projektu (opcjonalnie)", key="p_a")
                klient_awiz = st.text_input("Klient (Firma) *", placeholder="Wymagane", key="k_a")
                kto_przyjezdza = st.text_input("Kto fizycznie przyjedzie?", placeholder="np. Kurier DPD / Jan Kowalski")
                kontakt_awiz = st.text_input("Numer telefonu (opcjonalnie)", key="tel_a")

            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 10px 0;'>", unsafe_allow_html=True)
            if st.form_submit_button("Zapisz Awizację w Magazynie", type="primary"):
                if klient_awiz:
                    id_zadania = datetime.now().strftime("%Y%m%d%H%M%S")
                    akcja_format = f"Magazyn: {'Odbiór przez klienta' if 'odbiera' in typ_akcji_awiz else 'Zwrot przez klienta'} - {dzial_awiz}"
                    pelny_kontakt = f"{kontakt_awiz} | Przyjeżdża: {kto_przyjezdza}" if kto_przyjezdza else kontakt_awiz
                    # Automatycznie czyścimy zbędne pola, przypisujemy do Magazynu jako Awizacja
                    nowy_wiersz = [id_zadania, data_awiz.strftime("%Y-%m-%d"), godzina_awiz.strftime("%H:%M"), dzial_awiz, akcja_format, nr_projektu_awiz, klient_awiz, "MAGAZYN SQM", pelny_kontakt, "Odbiór własny", "Awizacja", "Łukasz (Magazyn)"]
                    database.dodaj_zadanie(nowy_wiersz)
                    st.toast("✅ Awizacja zapisana na tablicy magazynu!", icon="🏭")
                else:
                    st.error("Uzupełnij nazwę klienta!")

@st.fragment
def pokaz_zarzadzanie():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🛠️</span><span class="dashboard-title">Konsola Administracyjna</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Błyskawiczna zmiana statusów i edycja rekordów (bez przeładowania aplikacji).</div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    if dane:
        df = pd.DataFrame(dane)
        df['Data_sort'] = pd.to_datetime(df['Data'], format='%Y-%m-%d', errors='coerce')
        df = df.sort_values(by=['Data_sort', 'Godzina'], ascending=[False, True]).drop(columns=['Data_sort'])
        
        wyszukiwarka = st.text_input("🔍 Szukaj po nazwie klienta lub projekcie...", "")
        lista_opcji = (df['ID'].astype(str) + " | " + df['Data'].astype(str) + " | " + df['Klient'].astype(str) + " - " + df['Typ Akcji'].astype(str)).tolist()
        
        if wyszukiwarka:
            lista_opcji = [opcja for opcja in lista_opcji if wyszukiwarka.lower() in opcja.lower()]
            
        if len(lista_opcji) == 0:
            st.warning("Brak wyników wyszukiwania.")
            return
            
        wybor = st.selectbox("Wybierz rekord do przetworzenia:", ["-- Wybierz zadanie --"] + lista_opcji)
        
        if wybor != "-- Wybierz zadanie --":
            wybrane_id = wybor.split(" | ")[0]
            wiersz = df[df['ID'].astype(str) == wybrane_id].iloc[0]
            
            # --- SEKCJA: Szybka Zmiana Statusu ---
            st.markdown("### ⚡ Szybka Zmiana Statusu")
            aktualny_status = wiersz['Status']
            statusy_opcje = ["Nowe", "Zaakceptowane", "W drodze", "Zakończone", "Awizacja"]
            
            col_s1, col_s2 = st.columns([3, 1])
            with col_s1:
                nowy_status_szybki = st.selectbox(
                    "Wybierz nowy status", 
                    statusy_opcje, 
                    index=statusy_opcje.index(aktualny_status) if aktualny_status in statusy_opcje else 0,
                    label_visibility="collapsed"
                )
            with col_s2:
                if st.button("Aktualizuj Status", use_container_width=True):
                    database.aktualizuj_status(wybrane_id, nowy_status_szybki)
                    st.toast("Status zaktualizowany pomyślnie!", icon="✨")

            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 20px 0;'>", unsafe_allow_html=True)
            
            # --- SEKCJA: Pełna Edycja Danych ---
            st.markdown("### 📝 Pełna Edycja Danych")
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
                    n_status = st.text_input("Status (Ręcznie)", value=str(wiersz['Status']))
                    n_lokalizacja = st.text_input("Lokalizacja", value=str(wiersz['Lokalizacja']))
                    n_kontakt = st.text_input("Kontakt / Osoba", value=str(wiersz['Kontakt']))
                    n_wykonawca = st.text_input("Wykonawca", value=str(wiersz['Wykonawca']))
                
                if st.form_submit_button("Zapisz Zmiany"):
                    zaktualizowany_wiersz = [wiersz['ID'], n_data, n_godzina, n_dzial, wiersz['Typ Akcji'], wiersz['Nr Projektu'], n_klient, n_lokalizacja, n_kontakt, wiersz['Auto'], n_status, n_wykonawca]
                    database.edytuj_zadanie(wybrane_id, zaktualizowany_wiersz)
                    st.toast("Zmiany zapisane w bazie! 💾", icon="💾")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("📦 Przenieś do Archiwum", type="primary", use_container_width=True):
                    database.archiwizuj_zadanie(wybrane_id)
                    st.toast("Zlecenie przeniesione do archiwum!", icon="📦")
            with c2:
                if st.button("🗑️ Usuń bezpowrotnie", type="secondary", use_container_width=True):
                    database.usun_zadanie(wybrane_id)
                    st.toast("Rekord został trwale usunięty!", icon="🗑️")
    else:
        st.info("Brak zadań w bazie.")

@st.fragment
def pokaz_archiwum():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">📂</span><span class="dashboard-title">Archiwum Cyfrowe</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subheader">Pełen rejestr zakończonych operacji. Pobierane dynamicznie z bazy.</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Odśwież Dane z Chmury"):
        st.toast("Pobieram najnowsze dane...", icon="☁️")
    
    dane_archiwum = database.pobierz_archiwum()
    if dane_archiwum:
        df_arch = pd.DataFrame(dane_archiwum)
        if 'Data' in df_arch.columns and 'Godzina' in df_arch.columns:
             df_arch['Data_sort'] = pd.to_datetime(df_arch['Data'], format='%Y-%m-%d', errors='coerce')
             df_arch = df_arch.sort_values(by=['Data_sort', 'Godzina'], ascending=[False, False]).drop(columns=['Data_sort'])
        st.dataframe(style_df(df_arch.reset_index(drop=True).style), use_container_width=True, hide_index=True)
    else:
        st.info("Archiwum jest obecnie puste.")

@st.fragment
def pokaz_magazyn():
    st.markdown('<div class="dashboard-header"><span class="dashboard-title-icon">🏭</span><span class="dashboard-title">Logistyka Magazynowa</span></div>', unsafe_allow_html=True)
    
    dane = database.pobierz_wszystkie_dane()
    if not dane:
        st.info("Brak zadań w bazie.")
        return

    df = pd.DataFrame(dane)
    wybrana_data = st.date_input("Analizowany dzień:", datetime.now().date())
    df_dzien = df[df['Data'] == wybrana_data.strftime("%Y-%m-%d")]

    if df_dzien.empty:
        st.success(f"Brak ruchów sprzętowych na {wybrana_data}.")
        return

    df_dzien['Data_sort'] = pd.to_datetime(df_dzien['Data'], format='%Y-%m-%d', errors='coerce')
    df_dzien = df_dzien.sort_values(by=['Godzina']).drop(columns=['Data_sort'])

    df_wydania = df_dzien[df_dzien['Typ Akcji'].str.contains("Dowóz|Odbiór przez klienta", case=False)]
    df_przyjecia = df_dzien[df_dzien['Typ Akcji'].str.contains("Odbiór -|Zwrot przez klienta", case=False)]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="table-header" style="color: #e67e22; border-bottom: 2px solid #e67e22; padding-bottom:5px;">📤 DO WYDANIA (Szykujemy)</div>', unsafe_allow_html=True)
        for _, row in df_wydania.iterrows():
            opacity = "0.5" if row['Status'] == 'Zakończone' else "1"
            st.markdown(f"""
            <div class="card-container" style="opacity: {opacity}; display:block; padding:15px; border-left: 5px solid #e67e22; margin-bottom:15px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <strong style="font-size:1.2rem; color:#e67e22;">⏰ {row['Godzina']}</strong>
                    <span class="card-date-pill" style="background-color:rgba(230, 126, 34, 0.1); color:#e67e22; font-weight:bold;">🚚 {row['Wykonawca']} ({row['Auto']})</span>
                </div>
                <div style="font-size:0.95rem; margin-bottom:5px;"><strong>Projekt:</strong> {row['Nr Projektu']}</div>
                <div style="font-size:0.95rem; margin-bottom:5px;"><strong>Klient:</strong> {row['Klient']}</div>
                <div style="font-size:0.85rem; color:#94a3b8; margin-top:10px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 5px;"><strong>Akcja:</strong> {row['Typ Akcji']} | <strong>Status:</strong> {row['Status']}</div>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="table-header" style="color: #27ae60; border-bottom: 2px solid #27ae60; padding-bottom:5px;">📥 DO PRZYJĘCIA (Wraca)</div>', unsafe_allow_html=True)
        for _, row in df_przyjecia.iterrows():
            opacity = "0.5" if row['Status'] == 'Zakończone' else "1"
            st.markdown(f"""
            <div class="card-container" style="opacity: {opacity}; display:block; padding:15px; border-left: 5px solid #27ae60; margin-bottom:15px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <strong style="font-size:1.2rem; color:#27ae60;">⏰ {row['Godzina']}</strong>
                    <span class="card-date-pill" style="background-color:rgba(39, 174, 96, 0.1); color:#27ae60; font-weight:bold;">🚚 {row['Wykonawca']} ({row['Auto']})</span>
                </div>
                <div style="font-size:0.95rem; margin-bottom:5px;"><strong>Projekt:</strong> {row['Nr Projektu']}</div>
                <div style="font-size:0.95rem; margin-bottom:5px;"><strong>Klient:</strong> {row['Klient']}</div>
                <div style="font-size:0.85rem; color:#94a3b8; margin-top:10px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 5px;"><strong>Akcja:</strong> {row['Typ Akcji']} | <strong>Status:</strong> {row['Status']}</div>
            </div>""", unsafe_allow_html=True)
