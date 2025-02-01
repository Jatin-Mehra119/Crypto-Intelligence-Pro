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
            price_change = price_data['close'].pct_change(periods=vol).iloc[-1]
            prompt = f"""
            Analyze this market data:
            - Current Price: {price_data['close'].iloc[-1]:.2f}
            - {vol}D Volatility: {price_data['close'].pct_change().std():.2%}
            - Price Change in last {vol} Day: {price_change:.2%}
            - Market Sentiment: {sentiment_data['sentiment'].value_counts().to_dict()}
            
            Provide:
            1. Short-term (1 week) price prediction
            2. Key risk factors
            3. Recommended trading strategies
            4. Long-term outlook
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.5,
                max_tokens=5000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Insights generation failed: {str(e)}"