FROM python:3.11-slim

WORKDIR /app

# Install Streamlit dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir streamlit requests python-dotenv

# Copy application code
COPY app.py ./
COPY pages/ ./pages/

# Streamlit configuration
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check using Streamlit's built-in endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health', timeout=5)"

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
