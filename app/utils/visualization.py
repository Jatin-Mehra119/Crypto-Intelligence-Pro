import plotly.express as px

def plot_price_trend(data, title):
    """Plot price trend using Plotly"""
    return px.line(data, x='timestamp', y='close', title=title)

def plot_sentiment_distribution(data, title):
    """Plot sentiment distribution using Plotly"""
    return px.pie(data, names='sentiment', title=title)