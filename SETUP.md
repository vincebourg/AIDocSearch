# Milvus Vector Database Integration - Setup Guide

This guide will help you set up and test the RAG (Retrieval Augmented Generation) system with Milvus and OpenAI.

## Prerequisites

1. **Python 3.8+** installed
2. **Milvus server** running locally or remotely
3. **OpenAI API key** with access to embeddings and chat models

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `pymilvus` - Milvus Python client
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `beautifulsoup4` - HTML parsing
- `flask` - Web server
- `streamlit` - UI framework
- `requests` - HTTP client

### 2. Set Up Milvus

You have several options for running Milvus:

**Option A: Docker (Recommended)**
```bash
# Using Milvus Standalone
docker run -d --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest
```

**Option B: Milvus Lite (Embedded)**
```bash
pip install milvus
```
Then change `MILVUS_URI` in `.env` to a local file path:
```
MILVUS_URI="./milvus_demo.db"
```

**Option C: Zilliz Cloud (Managed Service)**
Sign up at https://cloud.zilliz.com and get your connection URI.

### 3. Configure Environment Variables

The `.env` file has been created with the following configuration:
```env
OPENAI_API_KEY="your-key-here"
MILVUS_URI="http://localhost:19530"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
OPENAI_CHAT_MODEL="gpt-4o-mini"
```

**Note:** Your `.env` file already contains an API key. Verify it's still valid.

### 4. Verify Milvus Connection

Check if Milvus is running:

```bash
# If using Docker
docker ps | grep milvus

# Test connection (if you have curl)
curl http://localhost:19530/healthz
```

## Testing the Implementation

### Test 1: Vector Store Functionality

Run the test script to verify vector store operations:

```bash
python test_vector_store.py
```

This will:
1. Connect to Milvus
2. Index documents from the `data/` folder
3. Perform test searches
4. Display results

Expected output:
```
============================================================
Vector Store Test
============================================================

Configuration:
  Milvus URI: http://localhost:19530
  Embedding Model: text-embedding-3-small
  API Key: ********************xxxx

1. Initializing vector store...
   ✓ Vector store initialized

2. Indexing documents from 'data' folder...
Loading consultation_fiscalite_2024.txt...
  Loaded 2 chunks from consultation_fiscalite_2024.txt
...
   ✓ Indexing complete

3. Testing search functionality...
   Query: 'What is the fiscal reform?'
   Found 2 relevant documents:
   ...

============================================================
✓ All tests passed!
============================================================
```

### Test 2: Flask Server

Start the server:

```bash
python server.py
```

Expected startup output:
```
Initializing vector store...
Connected to Milvus at http://localhost:19530
Collection 'legal_documents' already exists
Collection already contains 15 documents. Skipping indexing.
Server initialization complete. Starting Flask app...
 * Running on http://127.0.0.1:5000
```

### Test 3: Chat Endpoint

With the server running, test the `/chat` endpoint:

**Using curl:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the fiscal reform mentioned?"}'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:5000/chat",
    json={"message": "What is the fiscal reform mentioned?"}
)
print(response.json())
```

### Test 4: Health Check

Check server status:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "vector_store_ready": true,
  "documents_indexed": 15
}
```

### Test 5: Streamlit UI

If you have the Streamlit app (`app.py`), run it:

```bash
streamlit run app.py
```

Then interact with the chatbot through the web interface.

## Document Structure

The system indexes files from the `data/` folder:

- **Text files (.txt)**: Split into chunks of ~500 characters
- **HTML files (.html)**: Text extracted with BeautifulSoup, then chunked
- **CSV files (.csv)**: Each row converted to a text description

Current documents:
- `consultation_fiscalite_2024.txt`
- `contrat_commercial_partenaireA.txt`
- `historique_contentieux.csv`
- `jurisprudence_cassation2023.html`
- `mise_en_demeure_impaye_clientZ.txt`
- `note_droit_societes_2025.html`

## How It Works

### RAG Pipeline

1. **User sends question** → `/chat` endpoint
2. **Query embedding** → OpenAI converts question to vector
3. **Semantic search** → Milvus finds top 3 relevant document chunks
4. **Context building** → Retrieved chunks formatted as context
5. **LLM generation** → OpenAI generates answer using context
6. **Response returned** → User receives contextual answer

### Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Flask Server       │
│  (server.py)        │
└──────┬──────────────┘
       │
       ├──────────────┐
       ▼              ▼
┌──────────────┐  ┌───────────────┐
│ VectorStore  │  │ OpenAI API    │
│ (Milvus)     │  │ (Chat/Embed)  │
└──────────────┘  └───────────────┘
```

## Troubleshooting

### Issue: "Failed to connect to Milvus"

- Verify Milvus is running: `docker ps` or check your Milvus instance
- Check `MILVUS_URI` in `.env` matches your setup
- Try connecting directly: `curl http://localhost:19530/healthz`

### Issue: "OPENAI_API_KEY not found"

- Verify `.env` file exists in project root
- Check API key is properly quoted: `OPENAI_API_KEY="sk-..."`
- Test API key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"`

### Issue: "No documents found to index"

- Verify `data/` folder exists
- Check files have supported extensions: `.txt`, `.html`, `.csv`
- Ensure files are not empty

### Issue: "Rate limit exceeded"

- OpenAI has rate limits on API calls
- Reduce batch size in `vector_store.py` (line 205: `batch_size = 100` → `batch_size = 20`)
- Wait a moment before retrying

### Issue: "Collection already contains N documents"

This is expected behavior on subsequent runs. To force re-indexing:

```python
# In test_vector_store.py or server.py
vs.index_documents("data", force_reindex=True)
```

## Configuration Options

### Embedding Model

Change in `.env`:
```env
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"  # 1536 dimensions, faster, cheaper
OPENAI_EMBEDDING_MODEL="text-embedding-3-large"  # 3072 dimensions, more accurate
```

**Note:** Changing models requires re-indexing and updating `embedding_dim` in `vector_store.py:24`.

### Chat Model

Change in `.env`:
```env
OPENAI_CHAT_MODEL="gpt-4o-mini"      # Fast, cost-effective
OPENAI_CHAT_MODEL="gpt-4o"           # More capable
OPENAI_CHAT_MODEL="gpt-4-turbo"      # Even more capable
```

### Search Parameters

Modify `server.py:56`:
```python
relevant_docs = vector_store.search(message, top_k=3)  # Retrieve more/fewer chunks
```

### Chunking Strategy

Modify `vector_store.py:89`:
```python
chunks = self._chunk_text(text, chunk_size=500, overlap=50)  # Adjust sizes
```

## Next Steps

1. Add more documents to `data/` folder
2. Test with various legal questions
3. Tune `top_k` parameter for better results
4. Implement document update/deletion endpoints
5. Add metadata filtering (by document type, date, etc.)
6. Set up monitoring and logging

## API Reference

### POST /chat

**Request:**
```json
{
  "message": "Your question here"
}
```

**Response:**
```json
{
  "response": "AI-generated answer based on documents"
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

### GET /health

**Response:**
```json
{
  "status": "healthy",
  "vector_store_ready": true,
  "documents_indexed": 15
}
```

## Support

For issues with:
- **Milvus**: https://milvus.io/docs
- **OpenAI API**: https://platform.openai.com/docs
- **PyMilvus**: https://github.com/milvus-io/pymilvus
