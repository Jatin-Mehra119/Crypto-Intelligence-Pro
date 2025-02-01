import requests
import pandas as pd
import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(show_spinner=False)
def fetch_ohlc(coin_id: str, vs_currency: str, days: int):
    """
    Fetch OHLC data from CoinGecko with caching.
    
    Parameters:
      coin_id: Non-empty string representing cryptocurrency id.
      vs_currency: Currency code (e.g., 'usd', 'eur').
      days: Number of past days to fetch data for (must be a positive integer).
    """
    if not coin_id:
        logger.error("Received empty coin_id.")
        st.error("Please enter a valid cryptocurrency identifier. For valid identifiers see our community guidelines.")
        return pd.DataFrame()
    
    if days <= 0:
        logger.error(f"Invalid days parameter: {days}. It must be a positive integer.")
        st.error("Please choose a positive number of days.")
        return pd.DataFrame()
    
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {'vs_currency': vs_currency, 'days': days}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            logger.warning("Empty data returned from the API.")
            st.warning("No data available for the specified parameters.")
            return pd.DataFrame()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        st.error(f"Network error while fetching price data: {str(e)}")
    except ValueError as ve:
        logger.error(f"Data processing error: {str(ve)}")
        st.error("Error processing the received data.")
    except Exception as e:
        logger.exception("Unexpected error:")
        st.error(f"Unexpected error: {str(e)}")
    return pd.DataFrame()