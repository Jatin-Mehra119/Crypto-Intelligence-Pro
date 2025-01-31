import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Function to fetch OHLC data
def fetch_ohlc(coin_id, vs_currency, days):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc'
    params = {'vs_currency': vs_currency, 'days': days}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        ohlc_data = response.json()

        df = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None

# Streamlit UI
st.title("Cryptocurrency OHLC Data Viewer")

# User Inputs
coin_id = st.text_input("Enter Coin ID (e.g., bitcoin, dogecoin):", "dogecoin")
vs_currency = st.selectbox("Select Currency:", ["usd", "eur", "inr"], index=0)
days = st.selectbox("Select number of days:", [1, 2, 7, 14, 30, 90, 365], index=0)

# Fetch and display data
if st.button("Fetch Data"):
    df = fetch_ohlc(coin_id, vs_currency, days)

    if df is not None:
        st.subheader("OHLC Data Table")
        st.dataframe(df)

        # Candlestick Chart
        st.subheader("Candlestick Chart")
        fig = go.Figure(
            data=[go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="OHLC"
            )]
        )
        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig)
