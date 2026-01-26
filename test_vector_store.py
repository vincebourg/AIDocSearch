"""
Test script for vector store functionality.

This script tests the Milvus integration without running the full server.
Run with: python test_vector_store.py
"""

import os
from dotenv import load_dotenv
from vector_store import VectorStore

def main():
    # Load environment variables
    load_dotenv()

    print("=" * 60)
    print("Vector Store Test")
    print("=" * 60)

    # Get configuration
    openai_api_key = os.getenv("OPENAI_API_KEY")
    milvus_uri = os.getenv("MILVUS_URI", "http://localhost:19530")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY not found in .env file")
        return

    print(f"\nConfiguration:")
    print(f"  Milvus URI: {milvus_uri}")
    print(f"  Embedding Model: {embedding_model}")
    print(f"  API Key: {'*' * 20}{openai_api_key[-4:]}")

    try:
        # Initialize vector store
        print("\n1. Initializing vector store...")
        vs = VectorStore(
            milvus_uri=milvus_uri,
            openai_api_key=openai_api_key,
            embedding_model=embedding_model
        )
        print("   ✓ Vector store initialized")

        # Index documents
        print("\n2. Indexing documents from 'data' folder...")
        vs.index_documents("data")
        print("   ✓ Indexing complete")

        # Test search
        print("\n3. Testing search functionality...")
        test_queries = [
            "What is the fiscal reform?",
            "Tell me about commercial contracts",
            "What legal disputes are there?"
        ]

        for query in test_queries:
            print(f"\n   Query: '{query}'")
            results = vs.search(query, top_k=2)

            if results:
                print(f"   Found {len(results)} relevant documents:")
                for i, result in enumerate(results, 1):
                    print(f"\n   Result {i}:")
                    print(f"     Source: {result['source']}")
                    print(f"     Score: {result['score']:.4f}")
                    print(f"     Text: {result['text'][:100]}...")
            else:
                print("   No results found")

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
