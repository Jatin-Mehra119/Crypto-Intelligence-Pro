FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the required files
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Accept the secret token as a build argument
ARG GROQ_API_KEY

# Expose the secret GROQ_API_KEY build time and set them as environment variables
RUN --mount=type=secret,id=GROQ_API_KEY,mode=0444,required=true \
    export GROQ_API_KEY=$(cat /run/secrets/GROQ_API_KEY) && \
    echo "GROQ_API_KEY is set."

# Set the environment variable for runtime
ENV GROQ_API_KEY=${GROQ_API_KEY}

# Install Playwright and its dependencies
RUN playwright install 
RUN playwright install-deps

# Set environment variable for crawl4ai cache directory
ENV CRAWL4AI_CACHE_DIR="/app/.crawl4ai"

# Expose Streamlit port
EXPOSE 7860

# Ensure correct permissions for the cache directory
RUN mkdir -p /app/.crawl4ai && chmod 777 /app/.crawl4ai

# Run the Streamlit app
CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.port=7860", "--server.address=0.0.0.0"]