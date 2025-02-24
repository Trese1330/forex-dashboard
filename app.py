import yfinance as yf
import time
import pandas as pd
import ta  # For technical indicators
import streamlit as st
from datetime import datetime
import pytz

# Forex Pairs
FOREX_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURGBP", "EURAUD", "EURCAD", "EURCHF", "EURJPY", "GBPJPY",
    "GBPAUD", "GBPCAD", "GBPCHF", "AUDCAD", "AUDCHF", "AUDJPY",
    "CADJPY", "CHFJPY", "NZDJPY", "NZDCAD", "NZDCHF"
]

# Define Forex Sessions
def get_forex_session():
    """
    Determine which Forex session is active: Asian, London, New York.
    """
    tz = pytz.timezone('UTC')
    current_time = datetime.now(tz)

    if 0 <= current_time.hour < 9:  # Asian Session (Tokyo)
        return "Asian Session (Tokyo)"
    elif 9 <= current_time.hour < 17:  # London Session
        return "London Session"
    elif 17 <= current_time.hour < 24:  # New York Session
        return "New York Session"
    else:
        return "No Active Session"

# Fetch Forex Data
def fetch_forex_data(pair, interval="5m", period="7d"):
    """
    Fetch real-time forex price using Yahoo Finance.
    """
    symbol = pair + "=X"  # Construct symbol for Yahoo Finance
    try:
        data = yf.Ticker(symbol).history(period=period, interval=interval)

        if data.empty:
            print(f"⚠️ No data found for {pair}")
            return None

        return data
    except Exception as e:
        print(f"❌ Error fetching {pair}: {e}")
        return None

# Calculate Technical Indicators (SMA, EMA, RSI, MACD)
def calculate_technical_indicators(data):
    """
    Calculate technical indicators: SMA, EMA, RSI, MACD.
    """
    if data is None or data.empty:
        return None
    
    df = data.copy()

    # Simple Moving Average (SMA)
    df["SMA_50"] = ta.trend.sma_indicator(df["Close"], window=50)
    df["SMA_200"] = ta.trend.sma_indicator(df["Close"], window=200)

    # Exponential Moving Average (EMA)
    df["EMA_20"] = ta.trend.ema_indicator(df["Close"], window=20)

    # Relative Strength Index (RSI)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)

    # Moving Average Convergence Divergence (MACD)
    df["MACD"] = ta.trend.macd(df["Close"])
    df["MACD_Signal"] = ta.trend.macd_signal(df["Close"])

    return df

# Generate Trade Signal based on technical analysis
def generate_trade_signal(data):
    """
    Generate buy/sell signals based on SMA, RSI, and MACD strategy.
    """
    if data is None or data.empty:
        return "NO SIGNAL"

    last_row = data.iloc[-1]

    # Buy Signal: Price is above 50-SMA, RSI < 30 (Oversold), MACD crossover
    if last_row["Close"] > last_row["SMA_50"] and last_row["RSI"] < 30 and last_row["MACD"] > last_row["MACD_Signal"]:
        return "BUY ✅"

    # Sell Signal: Price is below 50-SMA, RSI > 70 (Overbought), MACD crossover
    elif last_row["Close"] < last_row["SMA_50"] and last_row["RSI"] > 70 and last_row["MACD"] < last_row["MACD_Signal"]:
        return "SELL ❌"

    else:
        return "HOLD ⚠️"

# Live Forex Updates Function
def live_forex_updates(pairs, interval="5m", period="7d", refresh_rate=60):
    """
    Fetch live forex updates and generate trade signals based on Forex session.
    """
    forex_data = {}

    # Create a container for Streamlit interface
    for pair in pairs:
        st.header(f"⚡ {pair} - {get_forex_session()}")
        
        # Fetch data for current session
        data = fetch_forex_data(pair, interval=interval, period=period)
        data = calculate_technical_indicators(data)
        
        # Generate trade signal based on the data
        signal = generate_trade_signal(data)
        latest_price = data["Close"].iloc[-1] if data is not None else "N/A"
        
        # Show the latest data in Streamlit
        st.write(f"Price: {latest_price:.4f}")
        st.write(f"Signal: {signal}")
        
        st.write("Technical Indicators:")
        st.write(f"RSI: {data['RSI'].iloc[-1]:.2f}")
        st.write(f"MACD: {data['MACD'].iloc[-1]:.2f}")
        st.write(f"SMA_50: {data['SMA_50'].iloc[-1]:.4f}")
        st.write(f"SMA_200: {data['SMA_200'].iloc[-1]:.4f}")
        st.write(f"EMA_20: {data['EMA_20'].iloc[-1]:.4f}")

        st.write("")

    st.write(f"⏳ Waiting {refresh_rate} seconds before next update...\n")
    time.sleep(refresh_rate)

# Streamlit App Function
def forex_dashboard():
    st.title("🔹 Forex Live Trading Signals 🔹")

    live_forex_updates(FOREX_PAIRS, interval="5m", period="7d", refresh_rate=60)

if __name__ == "__main__":
    forex_dashboard()
