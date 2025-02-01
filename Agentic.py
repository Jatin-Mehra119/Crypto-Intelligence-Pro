import os
import requests
import pandas as pd
import streamlit as st
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from groq import Groq
from pydantic import BaseModel
import json
import plotly.express as px

# Load environment variables
load_dotenv()

# Function to fetch OHLC data from CoinGecko
def fetch_ohlc(coin_id, vs_currency, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {'vs_currency': vs_currency, 'days': days}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        ohlc_data = response.json()
        df = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching OHLC data: {e}")
        return None
    
# Initialize Groq client
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

# --- Pydantic Models ---

class SentimentRequest(BaseModel):
    text: str
    context: str = "cryptocurrency market analysis"

class SentimentResponse(BaseModel):
    sentiment: str  # Positive, Neutral, Negative
    confidence: float
    key_terms: list[str]
    summary: str

# --- Crypto Analysis Core ---
class CryptoAnalyzer:
    def __init__(self):
        self.crawler = AsyncWebCrawler(config=BrowserConfig(headless=True))
        self.model_name = "llama-3.1-8b-instant"
        
    async def fetch_crypto_content(self, coin_name: str):
        """Fetch and process crypto-related content using crawl4ai"""
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=LLMExtractionStrategy(
                provider="groq",
                api_token=os.getenv("GROQ_API_KEY"),
                model_name=self.model_name,
                max_tokens=4000
            )
        )
        
        sources = [
            f"https://www.coindesk.com/search/?s={coin_name}",
            f"https://cointelegraph.com/search?query={coin_name}",
            f"https://news.google.com/search?q={coin_name}+cryptocurrency"
        ]
        
        articles = []
        for url in sources:
            result = await self.crawler.arun(url=url, config=config)
            articles.append({
                'source': url,
                'content': result.extracted_content,
                'markdown': result.markdown
            })
        return articles

    async def analyze_sentiment(self, content: str):
        """Analyze content sentiment using Groq"""
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this cryptocurrency content. Return sentiment (Positive/Neutral/Negative), 
                    confidence score (0-1), 3 key terms, and a 50-word summary. Format as JSON:
                    {content}"""
                }],
                model=self.model_name,
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            # Safely parse the JSON response
            response_data = json.loads(chat_completion.choices[0].message.content)
            
            # Ensure 'confidence' field is present, default to 0.5 if missing
            if 'confidence' not in response_data:
                response_data['confidence'] = 0.5
            
            return SentimentResponse(**response_data)
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return None

    async def generate_market_insights(self, sentiment_data: pd.DataFrame, price_data: pd.DataFrame):
        """Generate comprehensive market analysis using Groq"""
        try:
            # Prepare the prompt for market insights
            prompt = f"""
            Analyze this market data:
            - Current Price: {price_data['close'].iloc[-1]:.2f}
            - 30D Volatility: {price_data['close'].pct_change().std():.2%}
            - Market Sentiment: {sentiment_data['sentiment'].value_counts().to_dict()}
            
            Provide:
            1. Short-term (1 week) price prediction
            2. Key risk factors
            3. Recommended trading strategies
            4. Long-term outlook
            """
            
            # Get insights from Groq
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.5,
                max_tokens=500
            )
            
            # Return the generated insights
            return response.choices[0].message.content
        except Exception as e:
            return f"Insights generation failed: {str(e)}"

# --- Streamlit Dashboard ---
st.set_page_config(page_title="Crypto Intelligence Pro", layout="wide")

# Custom CSS styling
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
days = st.slider("Analysis Period (days):", 7, 365, 30)

# Initialize Analyzer
analyzer = CryptoAnalyzer()

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
                sentiment_results.append(analysis.dict())

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
                st.metric("30D Volatility", f"{ohlc_data['close'].pct_change().std():.2%}")
            
            # News Insights
            st.subheader("Critical Market Updates")
            for idx, (article, analysis) in enumerate(zip(articles, sentiment_results)):
                with st.expander(f"{analysis['summary'][:60]}... ({'⭐'*(idx+1)})"):
                    st.markdown(f"**Source**: {article['source']}")
                    st.markdown(f"**Sentiment**: `{analysis['sentiment']}` (Confidence: {analysis['confidence']:.0%})")
                    st.markdown(f"**Key Terms**: {', '.join(analysis['key_terms'])}")
                    st.markdown(f"**Summary**: {analysis['summary']}")
                    st.markdown(f"[Read Full Article]({article['source']})")

            # Predictive Insights
            st.subheader("AI-Powered Market Forecast")
            insights = asyncio.run(analyzer.generate_market_insights(sentiment_df, ohlc_data))
            st.markdown(insights)

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

async def generate_market_insights(self, sentiment_data: pd.DataFrame, price_data: pd.DataFrame):
    """Generate comprehensive market analysis"""
    prompt = f"""
    Analyze this market data:
    - Current Price: {price_data['close'].iloc[-1]:.2f}
    - 30D Volatility: {price_data['close'].pct_change().std():.2%}
    - Market Sentiment: {sentiment_data['sentiment'].value_counts().to_dict()}
    
    Provide:
    1. Short-term (1 week) price prediction
    2. Key risk factors
    3. Recommended trading strategies
    4. Long-term outlook
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model_name,
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Insights generation failed: {str(e)}"

if __name__ == "__main__":
    st.write("🌟 Configure your analysis parameters and click 'Run Advanced Analysis'")

