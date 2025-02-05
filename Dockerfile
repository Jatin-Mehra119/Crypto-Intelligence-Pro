# Use an official Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies required for building packages and for Playwright/crawl4ai
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libsqlite3-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create a non-root user and prepare directories with proper ownership
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p /app/.crawl4ai && chown -R appuser:appuser /app/.crawl4ai

# - The crawl4ai cache directory so that the library does not default to '/.crawl4ai' 
ENV CRAWL4AI_CACHE_DIR="/app/.crawl4ai"  
ENV PYTHONPATH=/app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project and ensure appuser owns all files
COPY . .
RUN chown -R appuser:appuser /app

# Install Playwright and its dependencies
RUN playwright install 
RUN playwright install-deps

# Expose the Streamlit port
EXPOSE 8080

# Switch to non-root user
USER appuser

# Ensure that the crawl4ai cache directory exists and is writable
RUN mkdir -p /app/.crawl4ai && chmod 777 /app/.crawl4ai

# Install Playwright browsers as appuser
RUN playwright install

# Set the default command to run your Streamlit application
CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.port=8080", "--server.address=0.0.0.0"]