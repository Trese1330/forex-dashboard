import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta

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

# 📏 Lot Size Calculator
st.subheader("💰 Lot Size Calculator")
balance = st.number_input("Account Balance ($)", value=1000)
risk_percent = st.number_input("Risk Percentage (%)", value=2)
stop_loss_pips = st.number_input("Stop Loss (Pips)", value=30)

if st.button("Calculate Lot Size"):
    risk_amount = (risk_percent / 100) * balance
    lot_size = risk_amount / (stop_loss_pips * 10)  # Assuming pip value = $10
    st.success(f"📏 Recommended Lot Size: {round(lot_size, 2)}")
