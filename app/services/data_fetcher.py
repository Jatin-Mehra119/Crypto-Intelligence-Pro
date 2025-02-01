import requests
import pandas as pd
import streamlit as st

def fetch_ohlc(coin_id: str, vs_currency: str, days: int):
    """Fetch OHLC data from CoinGecko"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {'vs_currency': vs_currency, 'days': days}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Price data error: {str(e)}")
        return pd.DataFrame()