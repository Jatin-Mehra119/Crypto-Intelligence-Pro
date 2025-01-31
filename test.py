import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import requests
from datetime import datetime

# Page config
st.set_page_config(page_title="Crypto Trading Dashboard", layout="wide")
st.title("Cryptocurrency Trading Dashboard")

# Sidebar controls
with st.sidebar:
    symbol = st.text_input("Trading Pair", "BTCUSDT").upper()
    interval = st.select_slider(
        "Timeframe",
        options=["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "1d"],
        value="1h"
    )
    data_points = st.slider("Number of candles", 50, 1000, 100)

def get_binance_ohlc(symbol, interval, limit=1000):
    url = "https://api.binance.com/api/v1/klines"
    params = {
        "symbol": symbol,
        "interval": interval,  # 1 second = "1s"
        "limit": limit,  # Number of data points
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Convert data into DataFrame for better readability
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df

# Get data
try:
    df = get_binance_ohlc(symbol, interval, data_points)
    
    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                open=df['open'].astype(float),
                high=df['high'].astype(float),
                low=df['low'].astype(float),
                close=df['close'].astype(float))])
    
    fig.update_layout(
        title=f'{symbol} Price Chart',
        yaxis_title='Price',
        xaxis_title='Time',
        template='plotly_dark'
    )

    # Display chart
    st.plotly_chart(fig, use_container_width=True)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"${float(df['close'].iloc[-1]):.2f}")
    with col2:
        price_change = float(df['close'].iloc[-1]) - float(df['close'].iloc[-2])
        st.metric("Price Change", f"${price_change:.2f}")
    with col3:
        st.metric("24h Volume", f"${float(df['volume'].iloc[-1]):,.2f}")
    with col4:
        st.metric("Number of Trades", int(df['number_of_trades'].iloc[-1]))

    # Display raw data
    if st.checkbox("Show Raw Data"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Error fetching data: {str(e)}")