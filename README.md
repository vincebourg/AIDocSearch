# Chatbot Streamlit App

This is a simple Streamlit application that allows users to send messages to a chatbot via a REST API.

## Prerequisites

1. **Python 3.8+** installed
2. **OpenAI API key** with access to embeddings and chat models

## Setup

1. Start milvus server
   on windows:
   ```
   ./standalone_embed.bat start
   ```
   OR
   on other shells:
   ```
   ./standalone_embed.sh start
   ```
2. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

3. Environment variables
   
   Duplicate .env.sample into .env and add your OpenAI API Key.

5. Run the chatbot server:
   ```
   python server.py
   ```

6. In a new terminal, run the Streamlit app:
   ```
   python -m streamlit run app.py
   ```

7. Open the Streamlit app in your browser (usually at http://localhost:8501).

## Usage

- Enter a message in the text input.
- Click "Send" to send the message to the chatbot.
- The chatbot's response will be displayed below.

## Docker Setup (Alternative)

### Prerequisites
- Docker Desktop installed
- Milvus running externally (use standalone_embed.bat or standalone_embed.sh)
- OpenAI API key

### Steps

1. **Start Milvus** (in separate terminal):
   ```bash
   # Windows
   .\standalone_embed.bat start

   # Linux/Mac
   ./standalone_embed.sh start
   ```

2. **Configure environment**:
   ```bash
   cp .env.sample .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Build and run containers**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Streamlit UI: http://localhost:8501
   - Flask API: http://localhost:5000
   - Health check: http://localhost:5000/health

### Docker Commands

**Start services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop services:**
```bash
docker-compose down
```

**Rebuild after code changes:**
```bash
docker-compose up --build
```

**Clean up everything:**
```bash
docker-compose down
docker system prune -f
```

### Development Mode
The docker-compose.yml is configured for development with:
- Source code mounted as volumes (hot reload on changes)
- Both containers exposed for debugging
- Streamlit auto-reload enabled

### Troubleshooting

**Container can't connect to Milvus:**
- Ensure Milvus is running: `docker-compose logs aidocsearch-server`
- Check MILVUS_URI in .env uses `http://host.docker.internal:19530`
- Windows: Ensure Docker Desktop allows host network access

**App can't reach server:**
- Check server is healthy: `curl http://localhost:5000/health`
- Verify server logs: `docker-compose logs aidocsearch-server`
