import streamlit as st
import requests
import pandas as pd

# API Key
API_KEY = "Y18YXNS3WP7F3Y92"

# List of major & minor currency pairs
currency_pairs = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF",
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "AUD/JPY", "NZD/USD", "EUR/AUD"
]

def fetch_forex_data(symbol):
    """Fetch forex data from Alpha Vantage API"""
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "FX_INTRADAY",
        "from_symbol": symbol.split("/")[0],  # Extract base currency
        "to_symbol": symbol.split("/")[1],    # Extract quote currency
        "interval": "5min",
        "apikey": API_KEY
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if "Time Series FX (5min)" not in data:
        return None

    df = pd.DataFrame(data["Time Series FX (5min)"]).T
    df.columns = ["Open", "High", "Low", "Close"]
    df.index = pd.to_datetime(df.index)
    return df

# Streamlit UI
st.title("📈 Forex Dashboard")

selected_pair = st.selectbox("Select Currency Pair", currency_pairs)

if st.button("Fetch Data"):
    forex_data = fetch_forex_data(selected_pair)
    if forex_data is not None:
        st.write(f"### Last 5 Entries for {selected_pair}")
        st.write(forex_data.head())
    else:
        st.error("Failed to fetch data. Check API limits.")
