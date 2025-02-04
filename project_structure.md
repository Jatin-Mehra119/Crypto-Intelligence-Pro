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
│   │   ├── data_fetcher.py     # Functions for fetching data
│   │   └── groq_client.py      # Groq client initialization and helper functions
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   └── visualization.py    # Visualization helper functions
│   └── config.py            # Configuration and environment variables
│
├── README_hf.md # Readem for huggingface space
├── requirements.txt         # List of dependencies
├── .env                     # Environment variables
└── README.md                # Project documentation
```