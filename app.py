import yfinance as yf
import pandas as pd
import ta
import streamlit as st
import pytz
import time

# List of major and minor forex pairs
currency_pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", 
                  "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "CADJPY=X"]

# Define the refresh rate in seconds (e.g., 60 seconds)
refresh_rate = 60

# Function to fetch forex data using yfinance
def fetch_data(symbol):
    data = yf.download(symbol, period="1d", interval="5m")
    return data

# Function to calculate technical indicators
def calculate_technical_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['MACD'] = ta.trend.MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9).macd()
    df['Signal'] = ta.trend.MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9).macd_signal()
    df['Upper_BB'], df['Lower_BB'] = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2).bollinger_hband(), ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2).bollinger_lband()
    return df

# Function to generate trade signals
def generate_trade_signal(df):
    signal = ""
    if df['RSI'].iloc[-1] < 30 and df['MACD'].iloc[-1] > df['Signal'].iloc[-1] and df['Close'].iloc[-1] < df['Lower_BB'].iloc[-1]:
        signal = "Buy"
    elif df['RSI'].iloc[-1] > 70 and df['MACD'].iloc[-1] < df['Signal'].iloc[-1] and df['Close'].iloc[-1] > df['Upper_BB'].iloc[-1]:
        signal = "Sell"
    return signal

# Streamlit Layout
st.title("Live Forex Dashboard")

# Countdown Timer
countdown = st.empty()  # Placeholder for countdown
while True:
    for seconds in range(refresh_rate, -1, -1):
        countdown.text(f"Refreshing in {seconds} seconds...")  # Show countdown
        time.sleep(1)
        
    # Fetch and update forex data for all currency pairs
    for pair in currency_pairs:
        df = fetch_data(pair)
        df = calculate_technical_indicators(df)
        signal = generate_trade_signal(df)
        
        st.subheader(f"{pair} Trading Signal")
        st.write(df.tail())
        st.write(f"Signal: {signal}")
        
    # Refresh the app
    st.experimental_rerun()  # This triggers a full page refresh after each cycle
