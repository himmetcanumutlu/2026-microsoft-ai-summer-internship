import os
import json
import subprocess

# Scanning settings
ALLOWED_EXTENSIONS = {'.md', '.py', '.txt', '.json'}
IGNORE_DIRS = {'.git', 'venv', '__pycache__', 'node_modules', '.idea', '.vscode', 'chroma_storage'}

# Chunking settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ChromaDB settings
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_storage")
COLLECTION_NAME = "project_docs"

# Foundry Local settings
EMBEDDING_MODEL = "qwen3-embedding-0.6b"
LLM_MODEL = "qwen3-0.6b"

# Retrieval settings
TOP_K = 3


def get_foundry_endpoint():
    """Return the Foundry Local base URL by querying the server status."""
    try:
        result = subprocess.run(
            ["foundry", "server", "status", "--output", "json"],
            capture_output=True, text=True, timeout=10
        )
        status = json.loads(result.stdout)
        if status.get("running") and status.get("webUrls"):
            return status["webUrls"][0]
    except Exception:
        pass
    return "http://localhost:9595"


def get_base_url():
    return f"{get_foundry_endpoint()}/v1"
