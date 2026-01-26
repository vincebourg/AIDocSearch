import os
import csv
from pathlib import Path
from typing import List, Dict
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from openai import OpenAI
from bs4 import BeautifulSoup


class VectorStore:
    def __init__(self, milvus_uri: str, openai_api_key: str, embedding_model: str):
        """
        Initialize the VectorStore with Milvus and OpenAI connections.

        Args:
            milvus_uri: URI for Milvus connection
            openai_api_key: OpenAI API key
            embedding_model: Name of OpenAI embedding model to use
        """
        self.milvus_uri = milvus_uri
        self.embedding_model = embedding_model
        self.collection_name = "legal_documents"
        self.embedding_dim = 1536  # text-embedding-3-small dimension

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=openai_api_key)

        # Connect to Milvus
        self._connect_milvus()

        # Initialize collection
        self.collection = self._get_or_create_collection()

    def _connect_milvus(self):
        """Establish connection to Milvus."""
        try:
            connections.connect(
                alias="default",
                uri=self.milvus_uri
            )
            print(f"Connected to Milvus at {self.milvus_uri}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Milvus: {e}")

    def _get_or_create_collection(self) -> Collection:
        """Get existing collection or create a new one."""
        if utility.has_collection(self.collection_name):
            print(f"Collection '{self.collection_name}' already exists")
            collection = Collection(self.collection_name)
            collection.load()
            return collection

        # Define collection schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim)
        ]

        schema = CollectionSchema(fields=fields, description="Legal documents collection")
        collection = Collection(name=self.collection_name, schema=schema)

        # Create index on embedding field
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        collection.load()

        print(f"Created collection '{self.collection_name}' with index")
        return collection

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks

        Returns:
            List of text chunks
        """
        # Split on double newlines (paragraphs) first
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If paragraph fits in current chunk
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(current_chunk)

                # If paragraph itself is too long, split it
                if len(para) > chunk_size:
                    words = para.split()
                    current_chunk = ""
                    for word in words:
                        if len(current_chunk) + len(word) + 1 <= chunk_size:
                            if current_chunk:
                                current_chunk += " " + word
                            else:
                                current_chunk = word
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = word
                else:
                    current_chunk = para

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _load_text_file(self, file_path: Path) -> List[Dict[str, str]]:
        """Load and chunk a text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        chunks = self._chunk_text(text)
        return [{"text": chunk, "source": file_path.name} for chunk in chunks]

    def _load_html_file(self, file_path: Path) -> List[Dict[str, str]]:
        """Load and chunk an HTML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator='\n\n', strip=True)

        chunks = self._chunk_text(text)
        return [{"text": chunk, "source": file_path.name} for chunk in chunks]

    def _load_csv_file(self, file_path: Path) -> List[Dict[str, str]]:
        """Load and convert CSV rows to text descriptions."""
        documents = []

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert each row to a formatted text description
                text_parts = []
                for key, value in row.items():
                    if value:
                        text_parts.append(f"{key}: {value}")

                text = ", ".join(text_parts)
                documents.append({"text": text, "source": file_path.name})

        return documents

    def _load_documents_from_folder(self, folder_path: str) -> List[Dict[str, str]]:
        """
        Load all documents from a folder.

        Args:
            folder_path: Path to folder containing documents

        Returns:
            List of document dictionaries with 'text' and 'source' keys
        """
        folder = Path(folder_path)
        all_documents = []

        for file_path in folder.iterdir():
            if file_path.is_file():
                print(f"Loading {file_path.name}...")

                if file_path.suffix == '.txt':
                    docs = self._load_text_file(file_path)
                elif file_path.suffix == '.html':
                    docs = self._load_html_file(file_path)
                elif file_path.suffix == '.csv':
                    docs = self._load_csv_file(file_path)
                else:
                    print(f"Skipping unsupported file type: {file_path.name}")
                    continue

                all_documents.extend(docs)
                print(f"  Loaded {len(docs)} chunks from {file_path.name}")

        return all_documents

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI API.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        response = self.openai_client.embeddings.create(
            input=texts,
            model=self.embedding_model
        )
        return [item.embedding for item in response.data]

    def index_documents(self, folder_path: str, force_reindex: bool = False):
        """
        Index documents from a folder into Milvus.

        Args:
            folder_path: Path to folder containing documents
            force_reindex: If True, clear existing data and reindex
        """
        # Check if collection already has data
        if not force_reindex and self.collection.num_entities > 0:
            print(f"Collection already contains {self.collection.num_entities} documents. Skipping indexing.")
            print("Use force_reindex=True to reindex all documents.")
            return

        # Load documents
        print(f"Loading documents from {folder_path}...")
        documents = self._load_documents_from_folder(folder_path)

        if not documents:
            print("No documents found to index.")
            return

        print(f"Total chunks to index: {len(documents)}")

        # Generate embeddings in batches
        batch_size = 100
        all_texts = []
        all_sources = []
        all_embeddings = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            texts = [doc["text"] for doc in batch]
            sources = [doc["source"] for doc in batch]

            print(f"Generating embeddings for batch {i // batch_size + 1}/{(len(documents) - 1) // batch_size + 1}...")
            embeddings = self._generate_embeddings(texts)

            all_texts.extend(texts)
            all_sources.extend(sources)
            all_embeddings.extend(embeddings)

        # Insert into Milvus
        print("Inserting documents into Milvus...")
        entities = [
            all_texts,
            all_sources,
            all_embeddings
        ]

        self.collection.insert(entities)
        self.collection.flush()

        print(f"Successfully indexed {len(documents)} document chunks")
        print(f"Collection now contains {self.collection.num_entities} documents")

    def index_single_file(self, file_path: Path, file_type: str) -> int:
        """
        Index a single file into Milvus.

        Args:
            file_path: Path to the file
            file_type: Type of file ('txt', 'html', 'csv')

        Returns:
            Number of chunks indexed
        """
        print(f"Loading {file_path.name}...")

        # Load document based on file type
        if file_type == 'txt':
            documents = self._load_text_file(file_path)
        elif file_type == 'html':
            documents = self._load_html_file(file_path)
        elif file_type == 'csv':
            documents = self._load_csv_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        if not documents:
            print("No content found in file.")
            return 0

        print(f"Loaded {len(documents)} chunks from {file_path.name}")

        # Generate embeddings
        texts = [doc["text"] for doc in documents]
        sources = [doc["source"] for doc in documents]

        print("Generating embeddings...")
        embeddings = self._generate_embeddings(texts)

        # Insert into Milvus
        print("Inserting documents into Milvus...")
        entities = [texts, sources, embeddings]
        self.collection.insert(entities)
        self.collection.flush()

        print(f"Successfully indexed {len(documents)} chunks")
        print(f"Collection now contains {self.collection.num_entities} documents")

        return len(documents)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """
        Search for relevant documents using semantic similarity.

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            List of relevant document chunks with source information
        """
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]

        # Search in Milvus
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["text", "source"]
        )

        # Format results
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "text": hit.entity.get("text"),
                    "source": hit.entity.get("source"),
                    "score": hit.distance
                })

        return formatted_results
