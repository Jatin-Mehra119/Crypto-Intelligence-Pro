# Use an official Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies required for building packages and for Playwright/crawl4ai
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libsqlite3-dev \
    sqlite3 \
    wget \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create a non-root user and prepare directories with proper ownership
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p /app/.crawl4ai && chown -R appuser:appuser /app/.crawl4ai

# Accept the secret token as a build argument
ARG GROQ_API_KEY

# Expose the secret GROQ_API_KEY at build time and set it as an environment variable
RUN --mount=type=secret,id=GROQ_API_KEY,mode=0444,required=true \
    export GROQ_API_KEY=$(cat /run/secrets/GROQ_API_KEY) && \
    echo "GROQ_API_KEY is set."

# Set environment variables for runtime:
# - The secret API key
# - The crawl4ai cache directory so that the library does not default to '/.crawl4ai'
ENV GROQ_API_KEY=${GROQ_API_KEY}  
ENV CRAWL4AI_CACHE_DIR="/app/.crawl4ai"  
ENV PYTHONPATH=/app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its browsers (as root)
RUN playwright install && \
    playwright install chromium && \
    playwright install-deps

# Copy the entire project and ensure appuser owns all files
COPY . .
RUN chown -R appuser:appuser /app

# Expose the Streamlit port
EXPOSE 7860

# Switch to non-root user
USER appuser

# Ensure that the crawl4ai cache directory exists and is writable
RUN mkdir -p /app/.crawl4ai && chmod 777 /app/.crawl4ai

# Set the default command to run your Streamlit application
CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.port=7860", "--server.address=0.0.0.0"]