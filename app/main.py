import streamlit as st
import asyncio
from app.services.crypto_analyzer import CryptoAnalyzer
from app.services.data_fetcher import fetch_ohlc
from app.config import groq_client
import pandas as pd
import plotly.express as px

# Custom CSS styling
st.set_page_config(page_title="Crypto Intelligence Pro", layout="wide", page_icon="₿")
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stPlotlyChart {border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .metric-box {padding: 20px; border-radius: 10px; background: white; margin: 10px;}
</style>
""", unsafe_allow_html=True)

# Dashboard Header
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://img.icons8.com/color/96/000000/bitcoin--v1.png", width=80)
with col2:
    st.title("Crypto Intelligence Pro")
    st.caption("Advanced Market Analysis & Predictive Insights")

# Main Inputs
coin_id = st.text_input("Enter Cryptocurrency:", "bitcoin").lower()
vs_currency = st.selectbox("Base Currency:", ["usd", "eur", "btc", "eth"])
days = st.selectbox("Analysis Period (days):", [7, 14, 30, 90, 365])

# Initialize Analyzer
analyzer = CryptoAnalyzer(groq_client)

if st.button("Run Advanced Analysis"):
    with st.spinner("🧠 Processing deep market analysis..."):
        # Fetch data
        articles = asyncio.run(analyzer.fetch_crypto_content(coin_id))
        ohlc_data = fetch_ohlc(coin_id, vs_currency, days)
        
        # Process sentiment analysis
        sentiment_results = []
        for article in articles:
            analysis = asyncio.run(analyzer.analyze_sentiment(article['content']))
            if analysis:
                sentiment_results.append(analysis.model_dump())

        # Generate visualizations
        if sentiment_results and not ohlc_data.empty:
            # Sentiment Analysis
            sentiment_df = pd.DataFrame(sentiment_results)
            
            # Price Analysis
            fig_price = px.line(ohlc_data, x='timestamp', y='close', 
                              title=f"{coin_id.upper()} Price Trend")
            
            # Sentiment Distribution
            fig_sentiment = px.pie(sentiment_df, names='sentiment', 
                                 title="Market Sentiment Distribution")
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_price, use_container_width=True)
            with col2:
                st.plotly_chart(fig_sentiment, use_container_width=True)
            
            # Key Metrics
            st.subheader("Market Health Indicators")
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("Current Price", f"${ohlc_data['close'].iloc[-1]:,.2f}")
            with mcol2:
                pos_percent = len(sentiment_df[sentiment_df['sentiment'] == 'Positive'])/len(sentiment_df)
                st.metric("Positive Sentiment", f"{pos_percent:.0%}")
            with mcol3:
                st.metric(f"{days}D Volatility", f"{ohlc_data['close'].pct_change().std():.2%}")
            
            # News Insights
            st.subheader("Critical Market Updates")
            for idx, (article, analysis) in enumerate(zip(articles, sentiment_results)):
                with st.expander(f"{analysis['summary'][:300]}... ({'⭐'*(idx+1)})"):
                    st.markdown(f"**Source**: {article['source']}")
                    st.markdown(f"**Sentiment**: `{analysis['sentiment']}` (Confidence: {analysis['confidence']:.0%})")
                    st.markdown(f"**Key Terms**: {', '.join(analysis['key_terms'])}")
                    st.markdown(f"**Summary**: {analysis['summary']}")
                    st.markdown(f"[Read Full Article]({article['source']})")

            # Predictive Insights
            st.subheader("AI-Powered Market Forecast")
            insights = asyncio.run(analyzer.generate_market_insights(sentiment_df, ohlc_data, days))
            st.markdown(insights)

if __name__ == "__main__":
    st.write("🌟 Configure your analysis parameters and click 'Run Advanced Analysis'")