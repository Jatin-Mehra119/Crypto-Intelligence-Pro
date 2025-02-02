import streamlit as st
import asyncio
from app.services.crypto_analyzer import CryptoAnalyzer
from app.services.data_fetcher import fetch_ohlc
from app.config import groq_client
import pandas as pd
import plotly.express as px
from app.utils.visualization import plot_price_trend, plot_sentiment_distribution

# Set page config and custom CSS styling
st.set_page_config(page_title="Crypto Intelligence Pro", layout="wide", page_icon="₿")
CUSTOM_CSS = """
<style>
    .main {background-color: #f8f9fa;}
    .stPlotlyChart {border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .metric-box {padding: 20px; border-radius: 10px; background: white; margin: 10px;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Dashboard Header
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://img.icons8.com/color/96/000000/bitcoin--v1.png", width=80)
with col2:
    st.title("Crypto Intelligence Pro")
    st.caption("Advanced Market Analysis & Predictive Insights")

# Main form for inputs
with st.form("analysis_form"):
    coin_id = st.text_input("Enter Cryptocurrency:", "bitcoin").lower().strip()
    vs_currency = st.selectbox("Base Currency:", ["usd", "eur", "btc", "eth"])
    days = st.selectbox("Analysis Period (days):", [7, 14, 30, 90, 365])
    submit_button = st.form_submit_button("Run Advanced Analysis")

if submit_button:
    if not coin_id:
        st.error("Please enter a valid cryptocurrency identifier.")
    else:
        analyzer = CryptoAnalyzer(groq_client)

        async def run_analysis():
            articles = await analyzer.fetch_crypto_content(coin_id)
            ohlc_data = fetch_ohlc(coin_id, vs_currency, days)
            sentiment_tasks = [analyzer.analyze_sentiment(article['markdown']) for article in articles]
            sentiment_results = await asyncio.gather(*sentiment_tasks)
            # Filter out any failed sentiment analyses
            sentiment_results = [s.model_dump() for s in sentiment_results if s]
            return articles, ohlc_data, sentiment_results

        with st.spinner("🧠 Processing deep market analysis..."):
            articles, ohlc_data, sentiment_results = asyncio.run(run_analysis())
            
            if ohlc_data.empty or not sentiment_results:
                st.error("Insufficient data available for analysis. Please check your inputs or try again later.")
            else:
                sentiment_df = pd.DataFrame(sentiment_results)
                
                # Price trend visualization
                fig_price = plot_price_trend(ohlc_data, f"{coin_id.upper()} Price Trend")
                # Sentiment distribution visualization
                fig_sentiment = plot_sentiment_distribution(sentiment_df, "Market Sentiment Distribution")
            
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
                    positive_count = len(sentiment_df[sentiment_df['sentiment'] == 'Positive'])
                    st.metric("Positive Sentiment", f"{(positive_count/len(sentiment_df)):.0%}")
                with mcol3:
                    st.metric(f"{days}D Volatility", f"{ohlc_data['close'].pct_change().std():.2%}")
                
                # News Insights
                st.subheader("Critical Market Updates")
                for idx, (article, analysis) in enumerate(zip(articles, sentiment_results)):
                    summary_preview = analysis['summary'][:300]
                    with st.expander(f"{summary_preview}... ({'⭐'*(idx+1)})"):
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