# Crypto Intelligence Pro

Crypto Intelligence Pro is an advanced market analysis tool for cryptocurrencies. It provides real-time price trends, sentiment analysis, technical indicators, and AI-powered market forecasts.

  

## Features

  

-  **Real-Time Data Fetching:** Retrieves historical OHLC price data from CoinGecko using cached API requests through [`app/services/data_fetcher.py`](app/services/data_fetcher.py).

-  **Sentiment Analysis:** Analyzes cryptocurrency-related news articles by fetching links and processing content via Groq AI Model in [`app/services/crypto_analyzer.py`](app/services/crypto_analyzer.py).

-  **Technical Analysis:** Computes technical indicators such as 7-day and 14-day SMAs, volatility, and price percentage changes to help determine market trends.

-  **Interactive Visualizations:** Displays dynamic charts using Plotly, including line, candlestick, OHLC, and pie charts for sentiment distribution ([app/utils/visualization.py](app/utils/visualization.py)).

-  **AI-Powered Market Forecasts:** Generates comprehensive market insights and predictions using Groq-powered AI models.

  

## Project Structure
```
crypto_intelligence_pro/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Main Streamlit app entry point
│   ├── models.py            # Pydantic models 
│   ├── services/            # Service layer for business logic
│   │   ├── __init__.py
│   │   ├── crypto_analyzer.py  # CryptoAnalyzer class
│   │   └──  data_fetcher.py     # Functions for fetching data 
│   │   
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   └── visualization.py    # Visualization helper functions 
│   └── config.py            # Configuration and environment variables 
│
├── README_hf.md # README for Hugging Face Space
├── requirements.txt         # List of dependencies
└── README.md                # Project documentation
```
  

## Usage

### 1. Clone the repository
- Use git to clone the project
```
git clone https://github.com/Jatin-Mehra119/Crypto-Dash.git
```
```
cd Crypto-Dash
```

### 2.  **Setup Environment:**

- Create a `.env` file with your Groq API key:

```
GROQ_API_KEY=your_api_key_here
```

- Install dependencies:

```
pip install -r requirements.txt
```
- Install Playwright and its dependencies
```
playwright install 
```
```
playwright install-deps
```

### 3.  **Run the Application:**

- Start the Streamlit app:

```
python -m streamlit run app/main.py
```

- Open [http://localhost:8501](http://localhost:8501) in your browser to use the APP.

  

## Continuous Integration/Deployment
- GitHub Actions workflow (.github/workflows/push_to_hf.yaml) automatically syncs the updated README and code changes to Hugging Face Spaces.

  

## Contributing
Contributions are welcome! Please open an issue or submit a pull request to improve the project.


## License
This project is licensed under the MIT License.