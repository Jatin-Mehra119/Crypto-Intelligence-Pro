import json
import pandas as pd
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from app.models import SentimentResponse
import streamlit as st
import os

class CryptoAnalyzer:
    def __init__(self, groq_client):
        self.crawler = AsyncWebCrawler(config=BrowserConfig(headless=True))
        self.model_name = "llama-3.1-8b-instant"
        self.groq_client = groq_client
        
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
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this cryptocurrency content. Return sentiment (Positive/Neutral/Negative), 
                    confidence score (0-1), 3 key terms, and a 300-word summary. Format as JSON:
                    {content}"""
                }],
                model=self.model_name,
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            response_str = chat_completion.choices[0].message.content
            try:
                response_data = json.loads(response_str)
            except json.JSONDecodeError as json_err:
                st.error(f"JSON decode error: {json_err}")
                return None
            
            if 'confidence' not in response_data:
                response_data['confidence'] = 0.5
            
            return SentimentResponse(**response_data)
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return None

    async def generate_market_insights(self, sentiment_data: pd.DataFrame, price_data: pd.DataFrame, vol: int):
        """Generate comprehensive market analysis using Groq"""
        try:
            # Validate vol parameter
            if vol <= 0:
                return "Error: 'vol' must be a positive integer."
            
            # Validate price_data has enough rows for calculations
            if len(price_data) < vol:
                return f"Error: Not enough data to calculate {vol}-day volatility. Only {len(price_data)} rows available."
            
            # Create a copy of price_data and preprocess it
            df = price_data.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Calculate 7-day and 14-day SMAs
            df['7-day SMA'] = df['close'].rolling(window=7).mean()
            df['14-day SMA'] = df['close'].rolling(window=14).mean()
            
            # Determine SMA crossover signals
            df['SMA_Crossover'] = None
            df.loc[df['7-day SMA'] > df['14-day SMA'], 'SMA_Crossover'] = 'Bullish'
            df.loc[df['7-day SMA'] < df['14-day SMA'], 'SMA_Crossover'] = 'Bearish'
            
            # Get the latest SMA crossover signal
            latest_sma_signal = df['SMA_Crossover'].iloc[-1]
            
            # Calculate additional metrics from the price data
            price_change_7d = df['close'].pct_change(periods=7).iloc[-1]
            price_change_30d = df['close'].pct_change(periods=30).iloc[-1]
            volatility = df['close'].pct_change().rolling(window=vol).std().iloc[-1]
            
            # Calculate sentiment distribution
            sentiment_distribution = sentiment_data['sentiment'].value_counts(normalize=True).to_dict()
            
            # Prepare the prompt with detailed metrics and SMA crossover insights
            prompt = f"""
            Analyze this market data:
            - Current Price: {df['close'].iloc[-1]:.2f}
            - 7D Price Change: {price_change_7d:.2%}
            - 30D Price Change: {price_change_30d:.2%}
            - {vol}D Volatility: {volatility:.2%}
            - Market Sentiment Distribution: {sentiment_distribution}
            - SMA Crossover Signal: {latest_sma_signal}
            
            Provide:
            1. Short-term (1 week) price prediction based on recent trends, sentiment, and SMA crossover signals.
            2. Key risk factors considering volatility, sentiment shifts, and SMA crossover signals.
            3. Recommended trading strategies based on current market conditions and SMA crossover signals.
            4. Long-term outlook considering historical performance, market sentiment, and SMA crossover signals.
            """
            
            # Generate the response using Groq
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.5,
                max_tokens=5000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Insights generation failed: {str(e)}"