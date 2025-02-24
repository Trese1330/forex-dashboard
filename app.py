import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from plyer import notification

# Initialize MT5
if not mt5.initialize():
    st.error("❌ MT5 initialization failed")
    quit()

st.title("📊 Forex Trading Live Dashboard")

# Forex pairs (Majors + Minors)
currency_pairs = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURGBP", "EURJPY", "EURCHF", "EURAUD", "EURNZD", "EURCAD",
    "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD",
    "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
    "CADJPY", "CADCHF", "CHFJPY", "NZDJPY", "NZDCHF"
]

# Timeframes
timeframes = {
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4
}

bars = 100  

# Function to calculate RSI
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Function to calculate MACD
def calculate_macd(data, short_period=12, long_period=26, signal_period=9):
    short_ema = data['close'].ewm(span=short_period, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_period, adjust=False).mean()
    macd_line = short_ema - long_ema
    return macd_line, macd_line.ewm(span=signal_period, adjust=False).mean()

# Function to generate buy/sell signals
def generate_trade_signal(data, pair, timeframe):
    if data is None or data.empty:
        return "NO DATA"

    rsi = data["RSI_14"].iloc[-1]
    macd = data["MACD"].iloc[-1]
    signal = data["Signal"].iloc[-1]
    close_price = data["close"].iloc[-1]

    if rsi < 30 and macd > signal:
        alert_message = f"📢 BUY SIGNAL: {pair} ({timeframe}) at {close_price}"
        notification.notify(title="📢 Forex Trading Signal", message=alert_message, timeout=10)
        return "BUY 📈"

    elif rsi > 70 and macd < signal:
        return "SELL 📉"

    return "HOLD ⏸️"

# Function to fetch live data
def fetch_live_data(symbol, timeframe_name, timeframe_value):
    rates = mt5.copy_rates_from_pos(symbol, timeframe_value, 0, bars)
    
    if rates is None or len(rates) == 0:
        return None

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")

    # Compute technical indicators
    df["RSI_14"] = calculate_rsi(df)
    df["MACD"], df["Signal"] = calculate_macd(df)

    return df

# Live Streamlit Dashboard
st.sidebar.header("Settings")
selected_pairs = st.sidebar.multiselect("Select Currency Pairs", currency_pairs, default=["EURUSD", "GBPUSD"])
selected_timeframe = st.sidebar.selectbox("Select Timeframe", list(timeframes.keys()))

if st.sidebar.button("Start Trading"):
    st.sidebar.success("📡 Streaming Live Data...")

    placeholder = st.empty()

    while True:
        table_data = []
        
        for pair in selected_pairs:
            df = fetch_live_data(pair, selected_timeframe, timeframes[selected_timeframe])
            signal = generate_trade_signal(df, pair, selected_timeframe)

            last_price = df["close"].iloc[-1] if df is not None and not df.empty else "N/A"
            table_data.append([pair, selected_timeframe, last_price, signal])

        df_table = pd.DataFrame(table_data, columns=["Pair", "Timeframe", "Price", "Signal"])
        placeholder.table(df_table)

        time.sleep(5)  # Refresh every 10 seconds
