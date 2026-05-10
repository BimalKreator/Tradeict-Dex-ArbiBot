import os

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/get-arbitrage-data",
)

st.set_page_config(page_title="Arbitrage Dashboard", layout="wide")

st_autorefresh(interval=3000, limit=None, key="data_refresh")

st.title("Real-Time Multi-Chain Arbitrage Dashboard")

try:
    response = requests.get(API_URL, timeout=15)
    response.raise_for_status()
except requests.exceptions.RequestException:
    st.error(
        "Backend API is currently starting or unavailable. Retrying in 3 seconds..."
    )
    st.stop()

data = response.json()

df = pd.DataFrame(data)

min_spread = st.sidebar.number_input(
    "Minimum Spread (%)",
    min_value=0.0,
    max_value=100.0,
    value=0.0,
    step=0.1,
)

if df.empty:
    st.info("No arbitrage data returned yet.")
else:
    filtered = df[df["spread_percentage"] >= min_spread].copy()

    filtered.columns = [
        col.replace("_", " ").title() for col in filtered.columns
    ]

    numeric_cols = filtered.select_dtypes(include="number").columns
    filtered[numeric_cols] = filtered[numeric_cols].round(4)

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )
