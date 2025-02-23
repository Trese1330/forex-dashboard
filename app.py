import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta
import datetime

# 📌 Streamlit Page Config
st.set_page_config(page_title="Forex Dashboard", layout="wide")

# 📌 Forex Pairs List
forex_pairs = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"]

# 📌 Sidebar - Pair Selector
pair = st.sidebar.selectbox("Select Forex Pair", forex_pairs, index=0)

# 📌 Function to Fetch Forex Data
@st.cache_data
def fetch_forex_data(pair):
    df = yf.download(pair, period="30d", interval="1h")
    df["SMA_50"] = ta.trend.sma_indicator(df["Close"], window=50)
    df["SMA_200"] = ta.trend.sma_indicator(df["Close"], window=200)
    df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
    return df

# 📌 Load Data
df = fetch_forex_data(pair)

# 📌 Fix the Shape Error
df["SMA_50"] = df["SMA_50"].values.ravel()
df["SMA_200"] = df["SMA_200"].values.ravel()
df["RSI"] = df["RSI"].values.ravel()

# 📊 Price Chart
st.subheader(f"📈 {pair} Price Chart")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close Price"))
fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], mode="lines", name="SMA 50", line=dict(dash="dot")))
fig.add_trace(go.Scatter(x=df.index, y=df["SMA_200"], mode="lines", name="SMA 200", line=dict(dash="dot")))
st.plotly_chart(fig, use_container_width=True)

# 📊 RSI Chart
st.subheader(f"📊 RSI Indicator")
rsi_fig = go.Figure()
rsi_fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))
rsi_fig.add_hline(y=70, line=dict(color="red", dash="dash"))
rsi_fig.add_hline(y=30, line=dict(color="green", dash="dash"))
st.plotly_chart(rsi_fig, use_container_width=True)

# 🔔 Forex Trading Sessions Notification
def get_current_session():
    now = datetime.datetime.utcnow().time()  # Get UTC time
    if datetime.time(7, 0) <= now <= datetime.time(16, 0):  # London Session (7AM - 4PM UTC)
        return "🕰️ London Session"
    elif datetime.time(13, 0) <= now <= datetime.time(22, 0):  # New York Session (1PM - 10PM UTC)
        return "🕰️ New York Session"
    elif datetime.time(0, 0) <= now <= datetime.time(9, 0):  # Tokyo Session (12AM - 9AM UTC)
        return "🕰️ Tokyo Session"
    elif datetime.time(22, 0) <= now <= datetime.time(7, 0):  # Sydney Session (10PM - 7AM UTC)
        return "🕰️ Sydney Session"
    else:
        return "⚠️ Out of Market Hours"

session_status = get_current_session()
st.sidebar.info(session_status)

# 📏 Lot Size Calculator
st.subheader("💰 Lot Size Calculator")
balance = st.number_input("Account Balance ($)", value=1000)
risk_percent = st.number_input("Risk Percentage (%)", value=2)
stop_loss_pips = st.number_input("Stop Loss (Pips)", value=30)

if st.button("Calculate Lot Size"):
    risk_amount = (risk_percent / 100) * balance
    lot_size = risk_amount / (stop_loss_pips * 10)  # Assuming pip value = $10
    st.success(f"📏 Recommended Lot Size: {round(lot_size, 2)}")

# 💡 Suggested Forex Pairs Based on Technical Indicators
st.subheader("📌 Suggested Trading Pairs")

def suggest_forex_pairs():
    suggestions = []
    for forex in forex_pairs:
        df_temp = fetch_forex_data(forex)
        if df_temp["RSI"].iloc[-1] < 30:
            suggestions.append(f"📉 **{forex} (Oversold, Potential Buy)**")
        elif df_temp["RSI"].iloc[-1] > 70:
            suggestions.append(f"📈 **{forex} (Overbought, Potential Sell)**")
    return suggestions

suggestions = suggest_forex_pairs()
if suggestions:
    for suggestion in suggestions:
        st.write(suggestion)
else:
    st.write("✅ No strong buy/sell signals at the moment.")
