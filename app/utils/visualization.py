import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 

def plot_price_trend(data, title):
    """Plot price trend using Plotly"""
    return px.line(data, x='timestamp', y='close', title=title)

def plot_sentiment_distribution(data, title):
    """Plot sentiment distribution using Plotly"""
    return px.pie(data, names='sentiment', title=title)

def plot_candlestick(data, title):
    """Plot candlestick chart using Plotly"""
    fig = go.Figure(data=[go.Candlestick(x=data['timestamp'],
                                         open=data['open'],
                                         high=data['high'],
                                         low=data['low'],
                                         close=data['close'])])
    fig.update_layout(title=title)
    return fig

def plot_ohlc(data, title):
    """Plot OHLC chart using Plotly"""
    fig = go.Figure(data=go.Ohlc(x=data['timestamp'],
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close']))
    fig.update_layout(title=title)
    return fig

# Show fetched data
def show_data(data):
    """Show fetched data using Streamlit components"""
    st.write(data)