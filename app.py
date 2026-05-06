import streamlit as st
import pandas as pd

# Konfiguracja strony
st.set_page_config(layout="wide", page_title="SQM DISPATCH Dashboard")

# --- CSS wstrzykiwany do Streamlit ---
local_css_string = """
/* Globalne tło głównego panelu - jasnoszara siatka */
.main {
    background-color: #f7f9fc;
    background-image: 
        linear-gradient(90deg, rgba(200,200,200,0.1) 1px, transparent 1px),
        linear-gradient(rgba(200,200,200,0.1) 1px, transparent 1px);
    background-size: 20px 20px;
    color: #333333;
}

/* Stylizacja paska bocznego (Sidebar) - głęboki granat */
section[data-testid="stSidebar"] {
    background-color: #1a2233 !important;
    color: #ffffff !important;
    padding-top: 1rem;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Stylizacja nagłówków w sidebar */
.sidebar-header {
    font-size: 1.2rem;
    font-weight: bold;
    padding: 0 1rem 1rem 1rem;
    border-bottom: 1px solid #3d495f;
    margin-bottom: 1rem;
}
.sidebar-subheader {
    font-size: 0.8rem;
    color: #8da1b3 !important;
    padding: 0 1rem 1.5rem 1rem;
}

/* Stylizacja menu bocznego */
.sidebar-menu-header {
    font-size: 0.75rem;
    color: #8da1b3 !important;
    padding: 0 1rem;
    margin-top: 1rem;
    text-transform: uppercase;
}
.sidebar-item {
    display: flex;
    align-items: center;
    padding: 10px 1rem;
    cursor: pointer;
    border-radius: 8px;
    margin: 4px 0.5rem;
    transition: background-color 0.2s;
    font-size: 0.9rem;
}
.sidebar-item:hover {
    background-color: #2b3a53;
}
.sidebar-item.selected {
    background-color: #2b3a53;
    color: #5d9cec !important;
    font-weight: bold;
}
.sidebar-item-icon {
    margin-right: 12px;
    font-size: 1.1rem;
}

/* Stylizacja Głównego Pulpitu */
.dashboard-header {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
}
.dashboard-title-icon {
    font-size: 1.8rem;
    margin-right: 10px;
    color: #8da1b3;
}
.dashboard-title {
    font-size: 1.8rem;
    font-weight: bold;
    color: #333;
}
.dashboard-subheader {
    font-size: 0.9rem;
    color: #6c757d;
    margin-bottom: 2rem;
}

/* Karty statystyk (Neomorfizm / Soft UI) */
.card-container {
    background: linear-gradient(145deg, #ffffff, #e6e6e6);
    border-radius: 15px;
    box-shadow: 20px 20px 60px #d9d9d9, -20px -20px 60px #ffffff;
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    transition: transform 0.2s;
}
.card-container:hover {
    transform: translateY(-3px);
}
.card-info {
    display: flex;
    flex-direction: column;
}
.card-title {
    font-size: 0.85rem;
    color: #6c757d;
    margin-bottom: 10px;
}
.card-value {
    font-size: 2.2rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 15px;
}
.card-date-pill {
    display: flex;
    align-items: center;
    background-color: rgba(93, 156, 236, 0.1);
    color: #5d9cec;
    border-radius: 15px;
    padding: 4px 10px;
    font-size: 0.75rem;
}
.card-date-icon {
    margin-right: 5px;
    font-size: 0.8rem;
}
.card-icon {
    font-size: 2.5rem;
}

/* Kolory pigułek daty dla poszczególnych kart */
.nowe .card-date-pill { background-color: rgba(230, 126, 34, 0.1); color: #e67e22; }
.w-trakcie .card-date-pill { background-color: rgba(241, 196, 15, 0.1); color: #f1c40f; }
.zakonczone .card-date-pill { background-color: rgba(39, 174, 96, 0.1); color: #27ae60; }

/* Tytuł tabeli */
.table-header {
    font-size: 1.1rem;
    font-weight: bold;
    color: #333;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

/* Tabela Pandas HTML */
.dataframe {
    border-radius: 10px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    background-color: white !important;
}

/* Stylizacja dolnego loginu w sidebar */
.sidebar-footer-login {
    position: fixed;
    bottom: 80px;
    left: 20px;
    color: #8da1b3 !important;
    font-size: 0.75rem;
}
"""
st.markdown(f'<style>{local_css_string}</style>', unsafe_allow_html=True)

# --- PANEL BOCZNY (Sidebar) ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">SQM DISPATCH</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subheader">Zalogowano jako: łukasz</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-menu-header">MENU</div>', unsafe_allow_html=True)
    
    # Customowe menu w HTML
    st.markdown('<div class="sidebar-item selected"><span class="sidebar-item-icon">⚙️</span> Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item"><span class="sidebar-item-icon">➕</span> Nowe Zlecenie</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item"><span class="sidebar-item-icon">🛠️</span> Zarządzanie Bazą</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-item"><span class="sidebar-item-icon">📂</span> Archiwum</div>', unsafe_allow_html=True)

    # Dolny przycisk wylogowania
    st.markdown('<div class="sidebar-footer-login">SQM DISPATCH<br>Zalogowano jako: łukasz</div>', unsafe_allow_html=True)
    if st.button("Wyloguj się", key="logout_sidebar"):
        st.write("Wylogowano.")

    # Wymuszenie stylu na przycisku Streamlita
    st.markdown(
        """
        <style>
        .stButton>button[key="logout_sidebar"] {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: calc(240px - 40px);
            background-color: #8e44ad !important;
            color: white !important;
            border-radius: 20px !important;
            border: none;
            font-size: 0.9rem;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# --- GŁÓWNY PANEL ---

# Nagłówek
st.markdown(
    '<div class="dashboard-header"><span class="dashboard-title-icon">⚙️</span><span class="dashboard-title">Dashboard</span></div>',
    unsafe_allow_html=True
)
st.markdown('<div class="dashboard-subheader">Przegląd zleceń i operacji na dziś</div>', unsafe_allow_html=True)

# Karty statystyk
cards = [
    {
        "class": "wszystkie-zlecenia",
        "title": "Wszystkie zlecenia",
        "value": 1,
        "date_icon": "📅",
        "date_text": "Dzisiaj (2026-05-06)",
        "card_icon": "📅"
    },
    {
        "class": "nowe",
        "title": "Nowe",
        "value": 0,
        "date_icon": "🔥",
        "date_text": "Dzisiaj (2026-05-06)",
        "card_icon": "🔥"
    },
    {
        "class": "w-trakcie",
        "title": "W trakcie",
        "value": 0,
        "date_icon": "🚜", 
        "date_text": "Dzisiaj (2026-05-06)",
        "card_icon": "🚜"
    },
    {
        "class": "zakonczone",
        "title": "Zakończone",
        "value": 0,
        "date_icon": "✅",
        "date_text": "Dzisiaj (2026-05-06)",
        "card_icon": "✅"
    }
]

# Renderowanie kart
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

# --- TABELA "ZLECENIA NA DZIŚ" ---
st.markdown('<div class="table-header">Zlecenia na dziś (2026-05-06)</div>', unsafe_allow_html=True)

# Przykładowe dane z ikonami Unicode (które świetnie działają jako proste grafiki w DataFrame)
data = {
    'ID': [20280306120218, 20260506130218, 20260506130220],
    'Data': ['2028-03-06', '2026-05-06', '2026-05-06'],
    'Godzina': ['12:01', '13:01', '13:01'],
    'Dział': ['Realizacja', 'Realizacja', 'Realizacja'],
    'Typ Akcji': ['Magazyn - Odbiór osobisty przez klienta', 'Magazyn - Odbiór osobisty przez klienta', '📦 Pakowanie, Projekt 3'],
    'Nr Projektu': [2, 2, 3],
    'Klient': ['🏢 klient testowy2', '🏢 klient testowy2', '🏢 klient testowy3'],
    'Lokalizacja': ['📍 gorsów', '📍 gorzów', '📍 Zielona Góra'],
    'Kontakt': ['📞 48555222333', '📞 48555222333', '📞 555123456'],
    'Auto': ['Brak', 'Brak', 'VW Crafter'],
    'Status': ['🟠 Awizacja', '🟠 Awizacja', '🔵 W Realizacji'],
    'Wykonawca': ['Łukasz (Magazyn)', 'Łukasz (Magazyn)', ''],
}
df = pd.DataFrame(data)

# Funkcja Pandas Styler do ostylowania nagłówków i co drugiego wiersza
def style_df(styler):
    styler.set_properties(**{'border-radius': '10px'})
    
    # Własny styl nagłówków tabeli
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
    
    # Zebrowanie - kolorowanie co drugiego wiersza na jasnoszaro
    def stripe_rows(row):
        return ['background-color: #f7f9fc' if row.name % 2 != 0 else 'background-color: white' for _ in row]
    
    styler.apply(stripe_rows, axis=1)
    return styler

# Renderowanie ostatecznej tabeli
styled_df = style_df(df.style)
st.dataframe(styled_df, use_container_width=True)
