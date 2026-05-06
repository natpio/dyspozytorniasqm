import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# 1. Konfiguracja uprawnień
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 2. Pobieranie poświadczeń z bezpiecznego sejfu Streamlit Secrets
try:
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=scopes
    )
    gc = gspread.authorize(credentials)

    # 3. Otwieranie arkusza
    arkusz = gc.open("AplikacjaKasprzak").worksheet("Arkusz1")
    dane = arkusz.get_all_records()
    df = pd.DataFrame(dane)
    
    st.success("Połączenie z Google Sheets zakończone sukcesem! 🎉")
    st.write("Oto podgląd naszej bazy danych:")
    st.dataframe(df)

except Exception as e:
    st.error(f"Wystąpił błąd podczas łączenia: {e}")
