import os
from dotenv import load_dotenv
from openai import OpenAI
from vector_store import VectorStore

# Load environment variables
load_dotenv()

# Initialize global variables
vector_store = None
openai_client = None

def initialize_services():
    """Initialize Milvus and OpenAI services."""
    global vector_store, openai_client

    # Get configuration from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    milvus_uri = os.getenv("MILVUS_URI", "http://localhost:19530")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    # Initialize OpenAI client
    openai_client = OpenAI(api_key=openai_api_key)

    # Initialize vector store
    print("Initializing vector store...")
    vector_store = VectorStore(
        milvus_uri=milvus_uri,
        openai_api_key=openai_api_key,
        embedding_model=embedding_model
    )

    # Index documents from data folder (only if collection is empty)
    data_folder = "data"
    if os.path.exists(data_folder):
        vector_store.index_documents(data_folder)
    else:
        print(f"Warning: Data folder '{data_folder}' not found. No documents to index.")

def generate_context(message):
    # Retrieve relevant context from vector store
    print(f"Searching for context for query: {message}")
    relevant_docs = vector_store.search(message, top_k=3)

    # Build context from retrieved documents
    context_parts = []
    for i, doc in enumerate(relevant_docs, 1):
        context_parts.append(f"[Document {i} - {doc['source']}]\n{doc['text']}")

    context = "\n\n".join(context_parts)
    return context

def ask_bot(message):

    context = generate_context(message)

    # Build prompt with context
    system_prompt = """You are a legal assistant. Use the following context to answer the question.
If the context doesn't contain relevant information, say so and provide a general response if possible."""

    user_prompt = f"""Context:
{context}

Question: {message}

Answer based on the context provided."""

    # Call OpenAI Chat API
    chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    completion = openai_client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    response = completion.choices[0].message.content
    return response

def bot_health_check():
    return {
        "status": "healthy",
        "vector_store_ready": vector_store is not None,
        "documents_indexed": vector_store.collection.num_entities if vector_store else 0
    }