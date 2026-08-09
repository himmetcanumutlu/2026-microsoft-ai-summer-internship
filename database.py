from chromadb.utils import embedding_functions
from config import CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL, get_base_url
import chromadb


class VectorStore:
    def __init__(self):
        base_url = get_base_url()
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key="not-needed",
            api_base=base_url,
            model_name=EMBEDDING_MODEL,
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def index_documents(self, documents):
        """Clear and rebuild the vector index from scanner documents."""
        if not documents:
            return 0

        self.client.delete_collection(name=COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

        ids = [str(i) for i in range(len(documents))]
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]

        self.collection.add(ids=ids, documents=texts, metadatas=metadatas)
        return len(documents)

    def query(self, question, top_k=3):
        """Return the top_k most relevant chunks for a question."""
        results = self.collection.query(query_texts=[question], n_results=top_k)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        sources = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            sources.append({
                "text": doc,
                "filename": meta.get("filename", "unknown"),
                "source_file": meta.get("source_file", "unknown"),
                "chunk_index": meta.get("chunk_index", 0),
                "score": round(1 - dist, 4) if dist else 0,
            })

        return sources

    def get_collection_stats(self):
        """Return the number of indexed chunks."""
        try:
            return self.collection.count()
        except Exception:
            return 0
