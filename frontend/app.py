import os

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

_arbitrage_url = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/get-arbitrage-data",
)
_base = _arbitrage_url.rstrip("/")
if _base.endswith("/get-arbitrage-data"):
    API_ROOT = _base[: -len("/get-arbitrage-data")].rstrip("/")
else:
    API_ROOT = _base

API_URL = (
    _arbitrage_url
    if _arbitrage_url.rstrip("/").endswith("/get-arbitrage-data")
    else f"{API_ROOT}/get-arbitrage-data"
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

with st.sidebar:
    min_spread = st.number_input(
        "Minimum Spread (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1,
    )

    st.header("Display Options")
    sort_order = st.radio(
        "Sort Spread By:",
        ["High to Low", "Low to High"],
    )

    st.header("API Fetch Filters")

    try:
        filters_resp = requests.get(f"{API_ROOT}/get-filters", timeout=10)
        filters_resp.raise_for_status()
        fetched_filters = filters_resp.json()
    except requests.exceptions.RequestException:
        fetched_filters = {"min_liquidity": 50000.0, "min_volume": 10000.0}

    if "min_liquidity_sidebar" not in st.session_state:
        st.session_state.min_liquidity_sidebar = float(
            fetched_filters["min_liquidity"]
        )
    if "min_volume_sidebar" not in st.session_state:
        st.session_state.min_volume_sidebar = float(
            fetched_filters["min_volume"]
        )

    st.number_input(
        "Minimum Liquidity ($)",
        min_value=0.0,
        step=1000.0,
        key="min_liquidity_sidebar",
    )
    st.number_input(
        "Minimum Volume ($)",
        min_value=0.0,
        step=1000.0,
        key="min_volume_sidebar",
    )

    if st.button("Apply API Filters"):
        payload = {
            "min_liquidity": float(st.session_state.min_liquidity_sidebar),
            "min_volume": float(st.session_state.min_volume_sidebar),
        }
        try:
            post_resp = requests.post(
                f"{API_ROOT}/update-filters",
                json=payload,
                timeout=15,
            )
            post_resp.raise_for_status()
            st.success("API filters updated successfully.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Failed to update filters: {exc}")

if df.empty:
    st.info("No arbitrage data returned yet.")
else:
    filtered = df[df["spread_percentage"] >= min_spread].copy()

    filtered.columns = [
        col.replace("_", " ").title() for col in filtered.columns
    ]

    ascending = True if sort_order == "Low to High" else False
    filtered = filtered.sort_values(
        by="Spread Percentage",
        ascending=ascending,
    )

    numeric_cols = filtered.select_dtypes(include="number").columns
    filtered[numeric_cols] = filtered[numeric_cols].round(4)

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )
