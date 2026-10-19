# Local README & Project Documentation RAG Assistant

This project was developed as part of the **Microsoft AI Innovators Summer Program**. If you'd like to read more, check out my [detailed post on LinkedIn](https://lnkd.in/p/dGUXVaAy). I'd love to hear your feedback. Feel free to connect!

---
**A fully offline Retrieval-Augmented Generation (RAG) chatbot powered by Microsoft Foundry Local — no internet, no cloud, no data leaks.**

---

## Project Metadata

| | |
|---|---|
| **Project Name** | Local README & Project Documentation RAG Assistant |
| **Author** | Himmet Can Umutlu |
| **Event** | Microsoft AI Innovators Summer Program 2026 |
| **Date** | August 8, 2026 |
| **Status** | Production Ready |
| **License** | MIT |

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [How RAG Works in This Project](#how-rag-works-in-this-project)
5. [Project Structure](#project-structure)
6. [Module Deep Dive](#module-deep-dive)
7. [Prerequisites](#prerequisites)
8. [Installation Guide](#installation-guide)
9. [Usage Guide](#usage-guide)
10. [Configuration Reference](#configuration-reference)
11. [System Flow Diagram](#system-flow-diagram)
12. [FAQ](#faq)
13. [Troubleshooting](#troubleshooting)
14. [Future Roadmap](#future-roadmap)

---

## Overview

This application scans your local project directories for code and documentation files (`.md`, `.py`, `.txt`, `.json`), splits them into semantic chunks, embeds them into a local vector database using **Foundry Local**-powered embeddings, and provides a **Streamlit** chat interface where you can ask natural-language questions about your project.

### Key Principles

| Principle | How It's Achieved |
|---|---|
| **100% Local** | All models run via Microsoft Foundry Local on your machine. No API keys, no cloud endpoints. |
| **Privacy-First** | Your source code never leaves your computer. Embeddings are stored in a local SQLite-backed database. |
| **Source-Traceable** | Every answer includes expandable citations showing exactly which file and chunk was used. |
| **Modular** | Four independent layers (Scanner, Database, LLM Client, UI) — each replaceable without touching the others. |
| **Lightweight** | ~1 GB total model size. Runs comfortably on any modern machine. |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app.py)                     │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │   Sidebar   │  │   Chat History   │  │  Citation Expander │  │
│  │  - Reindex  │  │  - User/Assist.  │  │  - Source Files    │  │
│  │  - Dir Pick │  │  - Markdown      │  │  - Similarity Score│  │
│  └─────────────┘  └──────────────────┘  └────────────────────┘  │
└──────────┬──────────────────────┬───────────────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────────┐  ┌──────────────────────────┐
│   scanner.py         │  │   llm_client.py          │
│   ───────────────    │  │   ───────────────        │
│   - os.walk()        │  │   - build_prompt()       │
│   - LangChain Text   │  │   - generate()           │
│     Splitter         │  │   - answer_question()    │
│   - Noise filtering  │  │   - OpenAI-compatible    │
│                      │  │     /v1/chat/completions │
└──────────┬───────────┘  └──────────┬───────────────┘
           │                         │
           ▼                         │
┌──────────────────────┐             │
│   database.py        │             │
│   ───────────────    │             │
│   - ChromaDB Persistent             │
│   - OpenAIEmbeddingFn│             │
│   - Cosine Similarity│             │
│   - HNSW Index       │             │
└──────────────────────┘             │
           │                         │
           ▼                         ▼
    ┌──────────────┐       ┌──────────────────────────┐
    │ chroma_storage│       │  Foundry Local Server    │
    │ (SQLite)      │       │  http://127.0.0.1:9595   │
    └──────────────┘       │                          │
                           │  ┌────────────────────┐  │
                           │  │ qwen3-0.6b         │  │
                           │  │ Chat Model (529 MB)│  │
                           │  └────────────────────┘  │
                           │  ┌────────────────────┐  │
                           │  │ qwen3-embedding    │  │
                           │  │ -0.6b (515 MB)     │  │
                           │  │ Embedding Model    │  │
                           │  └────────────────────┘  │
                           └──────────────────────────┘
```

### Layered Separation of Concerns

Each layer communicates only with its immediate neighbors:

1. **Presentation Layer** (`app.py`) — Streamlit UI, session state, user I/O
2. **Retrieval Layer** (`database.py`, `scanner.py`) — Document ingestion, chunking, vector search
3. **Generation Layer** (`llm_client.py`) — Prompt construction, Foundry Local API communication
4. **Infrastructure Layer** (Foundry Local, ChromaDB SQLite) — Model inference, persistent storage

---

## Technology Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| **LLM Runtime** | [Microsoft Foundry Local](https://github.com/microsoft/Foundry-Local) | 0.10.3 | Runs LLM and embedding models locally with GPU acceleration |
| **Chat Model** | Qwen3 0.6B | latest | Text generation from retrieved context |
| **Embedding Model** | Qwen3 Embedding 0.6B | latest | Converts text chunks to dense vectors for semantic search |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) | 1.5.9 | Stores and queries embeddings with metadata |
| **Text Splitting** | [LangChain Text Splitters](https://python.langchain.com/) | 1.1.2 | Recursive character-aware chunking |
| **UI Framework** | [Streamlit](https://streamlit.io/) | 1.61.1 | Web-based chat interface |
| **HTTP Client** | requests | 2.34.2 | REST calls to Foundry Local API |
| **Embedding Helper** | openai (Python SDK) | >=1.0.0 | Required by ChromaDB's OpenAIEmbeddingFunction |
| **API Protocol** | OpenAI-compatible | — | `/v1/chat/completions` and `/v1/embeddings` endpoints |
| **Embedding Distance** | Cosine similarity | — | Measures semantic closeness between vectors |
| **ANN Index** | HNSW (via ChromaDB) | — | Fast approximate nearest neighbor search |

### Why Each Technology?

- **Foundry Local**: Microsoft's on-device AI inference platform. GPU-accelerated, OpenAI-compatible REST API, automatic hardware detection (CUDA, OpenVINO, WebGPU), and one-command model management. Built specifically for Windows.
- **Qwen3 0.6B**: Alibaba's lightweight 0.6B parameter chat model — surprisingly capable for its size, GPU-accelerated via Foundry Local, responds in seconds not minutes.
- **Qwen3 Embedding 0.6B**: Purpose-built embedding model from Alibaba — 515 MB, fast embedding generation, strong semantic understanding for retrieval tasks.
- **ChromaDB**: Embedded vector database — no separate server process, just a SQLite file. Native OpenAI-compatible embedding function support. Metadata filtering for source tracking.
- **LangChain Text Splitters**: Recursive character splitting respects natural text boundaries (paragraphs, sentences) before falling back to character-level breaks.
- **Streamlit**: Fastest way to build a chat UI in Python. Session state management, built-in chat components, expandable containers for citations.
- **OpenAI SDK**: Used only as a wire protocol — ChromaDB's `OpenAIEmbeddingFunction` speaks OpenAI-format API, and Foundry Local speaks OpenAI-format API. No actual OpenAI account or key needed.

### Model Sizes

| Model | Size | Type |
|---|---|---|
| qwen3-0.6b | 529 MB | Chat (text generation) |
| qwen3-embedding-0.6b | 515 MB | Embedding (text to vector) |
| **Total** | **~1 GB** | |

---

## How RAG Works in This Project

RAG (Retrieval-Augmented Generation) combines **information retrieval** with **language model generation** to ground answers in real documents rather than model hallucination.

### The Five-Stage Pipeline

#### Stage 1: Document Scanning

```
Target Directory
     │
     ▼
os.walk() ──► Filter by extension (.md, .py, .txt, .json)
     │              Exclude noise dirs (.git, venv, __pycache__, ...)
     ▼
Read file contents (UTF-8)
```

- The scanner recursively walks the target directory
- Noisy directories are pruned in-place from the walk (not iterated)
- Files with allowed extensions are read as UTF-8 text
- Binary or unreadable files are gracefully skipped with a warning

#### Stage 2: Chunking

```
Raw Text File
     │
     ▼
RecursiveCharacterTextSplitter
     │  chunk_size=500 characters
     │  chunk_overlap=50 characters
     ▼
List of Chunks with Metadata
     │  {text, metadata: {source_file, filename, chunk_index}}
     ▼
ChromaDB Embedding
```

- LangChain's `RecursiveCharacterTextSplitter` splits text first by paragraphs (`\n\n`), then by lines (`\n`), then by sentences, and finally by characters
- 50-character overlap prevents meaning loss at chunk boundaries
- Each chunk carries full traceability metadata back to its source file

#### Stage 3: Vector Embedding & Indexing

```
Text Chunk ──► Foundry Local qwen3-embedding-0.6b ──► Dense Vector
                 POST /v1/embeddings                         │
                                                            ▼
                                                   ChromaDB Collection
                                                   ("project_docs")
                                                   HNSW Index + Cosine Distance
```

- Each chunk is sent to Foundry Local's `/v1/embeddings` endpoint
- qwen3-embedding-0.6b returns a dense vector embedding
- ChromaDB stores vectors with an HNSW (Hierarchical Navigable Small World) index
- Cosine similarity is used as the distance metric for semantic search
- All data persists in `./chroma_storage/` as SQLite

#### Stage 4: Semantic Retrieval

```
User Question
     │
     ▼
Embed with qwen3-embedding-0.6b ──► Query Vector
     │
     ▼
HNSW Nearest Neighbor Search ──► Top-K chunks (K=3)
     │  Cosine similarity ranking
     ▼
Retrieved Context Chunks
```

- The user's question is embedded using the same model that indexed the documents
- ChromaDB performs approximate nearest neighbor (ANN) search via HNSW
- Top 3 most semantically similar chunks are retrieved (configurable via `TOP_K`)
- Similarity scores are calculated as `1 - cosine_distance`

#### Stage 5: Answer Generation

```
System Prompt
   + Context Chunks (retrieved above)
   + User Question
     │
     ▼
Foundry Local /v1/chat/completions ──► qwen3-0.6b ──► Answer
                                                        │
                                                        ▼
                                                  Streamlit Chat UI
                                                  + Source Citations
```

- Retrieved chunks are formatted into a structured prompt with source annotations
- The prompt instructs the model to only use provided context and cite sources
- Foundry Local's OpenAI-compatible chat completions endpoint is used
- Each answer includes expandable citations with source files and similarity scores

### Why RAG Instead of Fine-Tuning?

| Approach | RAG (This Project) | Fine-Tuning |
|---|---|---|
| **Knowledge updates** | Re-scan — instant | Re-train — hours |
| **New projects** | Change directory, re-index | New model per project |
| **Source traceability** | Built-in (metadata) | Not possible |
| **Hardware needs** | Any machine with Foundry Local | GPU with 16GB+ VRAM |
| **Data privacy** | Guaranteed local | Guaranteed local |
| **Hallucination control** | Grounded in retrieved docs | Model still hallucinates |
| **Total model size** | ~1 GB | Depends on base model |

---

## Project Structure

```
readme-rag-project/
│
├── app.py                  # Streamlit web UI (chat interface, sidebar, citations)
├── scanner.py              # File system scanner + text chunker
├── database.py             # ChromaDB vector store wrapper (embed, index, query)
├── llm_client.py           # Foundry Local API client (prompt builder, chat completions)
├── config.py               # Centralized configuration (all tunable parameters)
├── requirements.txt        # Python package dependencies
│
├── chroma_storage/         # Persistent vector database (auto-created on first index)
│   └── chroma.sqlite3      # SQLite database with embeddings + metadata
│
├── venv/                   # Python virtual environment (git-ignored)
└── README.md               # This file
```

**Total: 4 source modules + 1 config + 1 UI — ~360 lines of Python.**

---

## Module Deep Dive

### `config.py` — Central Configuration

Every tunable parameter lives here. No magic numbers anywhere else.

```python
# Scanning filters
ALLOWED_EXTENSIONS = {'.md', '.py', '.txt', '.json'}
IGNORE_DIRS = {'.git', 'venv', '__pycache__', 'node_modules', '.idea', '.vscode', 'chroma_storage'}

# Chunking parameters
CHUNK_SIZE = 500        # Characters per chunk
CHUNK_OVERLAP = 50      # Overlap between consecutive chunks

# ChromaDB settings
CHROMA_PERSIST_DIR = "./chroma_storage"
COLLECTION_NAME = "project_docs"

# Foundry Local models
EMBEDDING_MODEL = "qwen3-embedding-0.6b"
LLM_MODEL = "qwen3-0.6b"

# Retrieval
TOP_K = 3               # Number of chunks to retrieve per query

# Dynamic endpoint discovery
get_foundry_endpoint()  # Queries "foundry server status" for the active port
get_base_url()          # Returns endpoint + /v1
```

**Key design decision**: The Foundry Local port is queried dynamically at startup via `foundry server status --output json` rather than hardcoded. This makes the app resilient to port changes across Foundry updates.

### `scanner.py` — File Scanner & Chunker

**Dependencies**: `config.py`, `langchain_text_splitters`

**Key Function**: `scan_and_chunk(target_directory)` → `List[dict]`

**Algorithm**:
1. Walk directory tree with `os.walk()`
2. Prune ignored directories in-place (`dirs[:] = [...]`)
3. For each file with an allowed extension, read as UTF-8
4. Pass content through `RecursiveCharacterTextSplitter` (500 chars, 50 overlap)
5. Append each chunk with its source metadata
6. Return complete document list

**Metadata per chunk**:
```python
{
    "text": "chunk content...",
    "metadata": {
        "source_file": "/absolute/path/to/file.py",
        "filename": "file.py",
        "chunk_index": 0
    }
}
```

### `database.py` — ChromaDB Vector Store

**Dependencies**: `config.py`, `chromadb`, `openai`

**Class**: `VectorStore`

| Method | Input | Output | Description |
|---|---|---|---|
| `__init__()` | — | — | Connects to persistent ChromaDB, creates/opens collection with OpenAI-compatible embedding function pointing at Foundry Local |
| `index_documents(documents)` | `List[dict]` | `int` (count) | Deletes old collection, creates fresh one, embeds and inserts all chunks |
| `query(question, top_k=3)` | `str, int` | `List[dict]` | Embeds question, runs ANN search, returns sources with similarity scores |
| `get_collection_stats()` | — | `int` | Returns total chunk count in collection |

**Embedding Function**: `OpenAIEmbeddingFunction` configured with `api_base=<foundry_endpoint>/v1` and `api_key="not-needed"`. Calls `POST /v1/embeddings` with model `qwen3-embedding-0.6b`.

**Index Type**: HNSW (Hierarchical Navigable Small World) — log(n) search complexity

**Re-indexing**: Clears the collection entirely and rebuilds from scratch. This ensures no stale chunks from deleted files remain.

### `llm_client.py` — Foundry Local API Client

**Dependencies**: `config.py`, `requests`, `re`

**Key Functions**:

- `strip_thinking(text)` — Removes `<think>...</think>` blocks from the reasoning model's output and cleans up common hallucination prefixes
- `build_prompt(question, sources)` — Builds a minimal prompt: for casual chat (no sources), sends just the user message; for questions with sources, formats them into a numbered document block with an instruction to answer only from the provided documents
- `generate(messages, model)` — POSTs to `<foundry_endpoint>/v1/chat/completions` with `stream: false`, `temperature: 0.1`, `max_tokens: 300`. Returns the cleaned response text after stripping thinking tags
- `answer_question(question, sources, model)` — Glue function: builds prompt then generates response

**API Endpoint**: `POST /v1/chat/completions` (OpenAI-compatible)

**Prompt Strategy (no sources — casual chat)**:
```
[{"role": "user", "content": "merhaba"}]
```
No system prompt — the model responds naturally to greetings without hallucinating about documents.

**Prompt Strategy (with sources — RAG question)**:
```
Answer this question using ONLY the information below.

=== DOCUMENTS ===
[1] filename.py:
<chunk text>

[2] another.md:
<chunk text>
=== END DOCUMENTS ===

QUESTION: <user question>

ANSWER:
```

**Generation Parameters**:

| Parameter | Value | Why |
|---|---|---|
| `temperature` | 0.1 | Low temperature reduces hallucination — critical for a small model doing RAG |
| `max_tokens` | 300 | Keeps responses concise and prevents rambling |
| `stream` | false | Synchronous response for simplicity |

**Error Handling**:
- Connection refused → warns user to start Foundry Local
- Timeout (120s) → asks user to retry
- Generic errors → passes error message through

### `app.py` — Streamlit Chat Interface

**Dependencies**: `config.py`, `scanner.py`, `database.py`, `llm_client.py`

**Session State Variables**:

| Variable | Type | Purpose |
|---|---|---|
| `messages` | `list[dict]` | Full chat history (role, content, sources) |
| `vector_store` | `VectorStore` | Persistent database connection |
| `indexed` | `bool` | Whether current directory has been indexed |

**Layout**:

**Sidebar (left)**:
- Directory path input (defaults to project root)
- "Projeyi Yeniden Tara & Indeksle" (Re-scan & Re-index) button
- Chunk count metric display
- Privacy notice

**Main Area (center)**:
- Chat message history (user/assistant messages)
- Chat input box at the bottom
- Each assistant message has an expandable **"Kullanilan Kaynaklar (Citations)"** section showing:
  - Source filename with chunk index
  - Similarity score
  - Full file path
  - Raw chunk content

**Streamlit UI Components Used**:

| Component | What It Does |
|---|---|
| `st.set_page_config` | Sets browser tab title ("Yerel RAG Asistanı") and wide layout |
| `st.chat_input` | Chat input box at the bottom of the page |
| `st.chat_message` | Chat bubbles — user messages and assistant replies |
| `st.sidebar` | Left sidebar panel for controls |
| `st.text_input` | Directory path text field in the sidebar |
| `st.button` | "Projeyi Yeniden Tara & Indeksle" primary action button |
| `st.expander` | Expandable "Kullanılan Kaynaklar (Citations)" section below each answer |
| `st.spinner` | "Düşünüyor..." / "Dosyalar taranıyor..." loading animations |
| `st.metric` | Indexed chunk count display in the sidebar |
| `st.success` / `st.info` / `st.warning` / `st.error` | Status/info/warning/error message banners |
| `st.code` | Raw chunk content display in monospace font |
| `st.markdown` | Rendered markdown for chat messages and source labels |
| `st.caption` | Small text for file path display under source entries |
| `st.session_state` | Persists chat history, vector store connection, and index state across reruns |

The entire UI is built with **zero HTML/CSS/JavaScript** — pure Python via Streamlit. The app runs at **http://localhost:8501**.

---

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Disk Space | ~1.5 GB (models) + 100 MB (app) | Same |
| CPU | Any x86_64 | Any modern 4+ core |
| GPU | Not required, but beneficial | NVIDIA 2000+ series or AMD 6000+ series |

With Foundry Local's automatic GPU detection, models run on GPU if available, falling back to CPU otherwise. Total model footprint is only ~1 GB.

### Software Requirements

| Software | Version | How to Install |
|---|---|---|
| **Python** | 3.10–3.13 | [python.org](https://www.python.org/downloads/) or `winget install Python.Python.3.12` |
| **Microsoft Foundry Local** | 0.10+ | `winget install Microsoft.FoundryLocal` or [GitHub releases](https://github.com/microsoft/Foundry-Local/releases) |
| **Git** (optional) | any | [git-scm.com](https://git-scm.com/download/win) |

### Required Models (downloaded automatically in setup)

| Model | Size | Type | Command |
|---|---|---|---|
| `qwen3-0.6b` | 529 MB | Chat (text generation) | `foundry model download qwen3-0.6b` |
| `qwen3-embedding-0.6b` | 515 MB | Embedding (text to vector) | `foundry model download qwen3-embedding-0.6b` |

---

## Installation Guide

### Step 1: Clone or Download the Project

```bash
git clone <repo-url> readme-rag-project
cd readme-rag-project
```

Or simply extract the project folder to any location.

### Step 2: Install Microsoft Foundry Local

Open PowerShell or Command Prompt as Administrator:

```powershell
# Method 1: Winget (recommended, easiest)
winget install Microsoft.FoundryLocal

# Method 2: Manual MSIX download
# Download from https://github.com/microsoft/Foundry-Local/releases/latest
# Get the x64 .msix file and the VCLibs dependency, then:
# Add-AppxPackage .\FoundryLocal.msix -DependencyPath .\VcLibs.appx
```

Close and reopen your terminal, then verify:

```bash
foundry --version
```

Expected: `0.10.3` (or newer)

### Step 3: Download Foundry Local Models

```bash
# Chat model — text generation (529 MB)
foundry model download qwen3-0.6b

# Embedding model — text to vector (515 MB)
foundry model download qwen3-embedding-0.6b
```

Load the models into memory:

```bash
foundry model load qwen3-0.6b
foundry model load qwen3-embedding-0.6b
```

Verify they are loaded:

```bash
foundry model list
```

Expected output shows both models with status indicators.

### Step 4: Configure Foundry Local Port (Optional)

Foundry Local uses a random port by default. The app auto-discovers the port at startup, but if you prefer a fixed port:

```bash
foundry config set port 9595 --force
foundry server restart
```

### Step 5: Create Python Virtual Environment

```bash
cd readme-rag-project

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 6: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:

| Package | Version | Purpose |
|---|---|---|
| `chromadb` | >=0.5.0 | Vector database with OpenAI embedding support |
| `langchain-text-splitters` | >=0.3.0 | Recursive character text splitting |
| `streamlit` | >=1.35.0 | Web-based chat UI |
| `requests` | >=2.32.0 | HTTP client for Foundry Local API |
| `openai` | >=1.0.0 | Required by ChromaDB's OpenAIEmbeddingFunction for Foundry Local compatibility |

### Step 7: Run the Application

Make sure Foundry Local is running with models loaded:

```bash
# Check server status
foundry server status

# If not running:
foundry server start
foundry model load qwen3-0.6b
foundry model load qwen3-embedding-0.6b
```

Then start the Streamlit app:

```bash
streamlit run app.py
```

Open your browser to **http://localhost:8501**.

---

## Usage Guide

### First-Time Setup

1. Open `http://localhost:8501` in your browser
2. In the **sidebar**, confirm the target directory (defaults to the project folder itself)
3. Click **"Projeyi Yeniden Tara & Indeksle"** (Re-scan & Re-index)
4. Wait for the scan to complete — you'll see a green success message with the chunk count
5. Start asking questions in the chat box

### Asking Questions

Ask natural-language questions about your codebase:

```
"How do I set up this project?"
"What does the scanner.py module do?"
"Which configuration parameters control chunking?"
"Explain the database schema used in this project."
"What are the main classes and their methods?"
```

### Understanding Responses

Each response includes:
- **Answer text** — generated by qwen3-0.6b based on retrieved context
- **"Kullanilan Kaynaklar (Citations)" expander** — click to see:
  - Source filename and chunk index
  - Cosine similarity score (1.0 = perfect match, 0.0 = no relation)
  - Absolute file path
  - Raw chunk content

### Re-indexing

Whenever your code changes:
1. Click **"Projeyi Yeniden Tara & Indeksle"** in the sidebar
2. The old index is deleted and a fresh one is built
3. Previous chat history is cleared

### Scanning a Different Project

1. Change the directory path in the sidebar
2. Click **"Projeyi Yeniden Tara & Indeksle"**
3. Now questions are answered from the new project's documentation

### Chat History

- Messages persist across re-indexes within the same session
- Re-indexing clears history (since old chunks are gone)
- Refreshing the browser resets the session

---

## Configuration Reference

All settings are in `config.py`. Modify this file before starting the app.

### Scanning

| Parameter | Default | Description |
|---|---|---|
| `ALLOWED_EXTENSIONS` | `{'.md', '.py', '.txt', '.json'}` | File extensions to include |
| `IGNORE_DIRS` | `{'.git', 'venv', '__pycache__', 'node_modules', '.idea', '.vscode', 'chroma_storage'}` | Directories to skip |

### Chunking

| Parameter | Default | Range | Effect |
|---|---|---|---|
| `CHUNK_SIZE` | 500 | 200–2000 | Larger = more context per chunk but less precise retrieval |
| `CHUNK_OVERLAP` | 50 | 0–200 | Larger = less meaning loss at boundaries but more storage |

### Models

| Parameter | Default | Alternatives |
|---|---|---|
| `LLM_MODEL` | `qwen3-0.6b` | `qwen3-1.7b`, `qwen3-4b`, `phi-3.5-mini`, `phi-4-mini` |
| `EMBEDDING_MODEL` | `qwen3-embedding-0.6b` | `qwen3-embedding-8b` |

To use a different model, download and load it first:
```bash
foundry model download qwen3-1.7b
foundry model load qwen3-1.7b
```
Then change `LLM_MODEL = "qwen3-1.7b"` in `config.py`.

### Available Foundry Local Models (subset)

| Model | Size | Best For |
|---|---|---|
| `qwen3-0.6b` | 529 MB | Fastest, smallest — ideal for RAG |
| `qwen3-1.7b` | 1.4 GB | Good balance of speed and quality |
| `phi-3.5-mini` | 1.9 GB | Strong reasoning, compact |
| `phi-4-mini` | 2.2 GB | Latest Phi model, excellent quality |
| `qwen3-embedding-0.6b` | 515 MB | Fast embeddings |
| `qwen3-embedding-8b` | 6.0 GB | High quality embeddings (needs more RAM) |

### Retrieval

| Parameter | Default | Range | Effect |
|---|---|---|---|
| `TOP_K` | 3 | 1–10 | More chunks = more context but slower generation and potential distraction |

### Storage

| Parameter | Default | Description |
|---|---|---|
| `CHROMA_PERSIST_DIR` | `./chroma_storage` | Where vector database files are stored |
| `COLLECTION_NAME` | `project_docs` | ChromaDB collection identifier |

### Dynamic Endpoint Discovery

The app **auto-discovers** Foundry Local's port at startup by calling:
```bash
foundry server status --output json
```
This returns the current endpoint (`http://127.0.0.1:<port>`) and is handled by `get_foundry_endpoint()` in `config.py`. No port hardcoding needed.

---

## System Flow Diagram

```
USER ACTION                        SYSTEM PROCESS
════════════                       ══════════════════

1. Set directory path      ──►     config.py reads target path
                                   │
2. Click "Re-scan"         ──►     scanner.py::scan_and_chunk()
                                   │  - os.walk() directory tree
                                   │  - Filter files by extension
                                   │  - RecursiveCharacterTextSplitter
                                   │  - Return List[dict]
                                   ▼
3. (automatic)             ──►     database.py::index_documents()
                                   │  - Delete old collection
                                   │  - Create new collection
                                   │  - Embed each chunk via
                                   │    qwen3-embedding-0.6b
                                   │  - POST /v1/embeddings
                                   │  - Store in chroma_storage/
                                   ▼
4. (index complete)        ◄──     UI shows chunk count metric
                                   │
5. Type question           ──►     database.py::query()
                                   │  - Embed question
                                   │  - HNSW search (cosine similarity)
                                   │  - Return top_k=3 chunks
                                   ▼
6. (automatic)             ──►     llm_client.py::answer_question()
                                   │  - build_prompt(question, sources)
                                   │  - POST /v1/chat/completions
                                   │  - qwen3-0.6b generates answer
                                   │  - Return generated text
                                   ▼
7. See answer + sources    ◄──     Streamlit renders markdown
                                   + expandable citation cards
```

---

## FAQ

### Q: Does this send my code to any external server?

**No.** Every component runs on your computer:
- Foundry Local runs models locally (`127.0.0.1:9595`)
- ChromaDB stores vectors in a local SQLite file (`chroma_storage/`)
- Streamlit runs the web server locally (`localhost:8501`)
- The `openai` Python package is used only as a wire protocol compatibility layer — zero data leaves your machine

### Q: Can I use this without a GPU?

**Yes.** Foundry Local auto-detects hardware and falls back to CPU if no GPU is available. The models are small enough (~1 GB total) to run on CPU-only machines. With GPU, responses are near-instant.

### Q: Why qwen3-0.6b instead of a larger model?

The 0.6B parameter model was chosen deliberately:
1. **Size**: 529 MB — fits in GPU memory alongside the embedding model
2. **Speed**: Near-instant responses on GPU, acceptable on CPU
3. **Quality**: Surprisingly capable for document-grounded Q&A when given good context
4. **RAG advantage**: In RAG, answer quality depends more on retrieval quality than model size. A small model with good context outperforms a large model hallucinating.

### Q: Can I swap in a larger model?

Yes! Edit `LLM_MODEL` in `config.py`. Popular alternatives:

```bash
foundry model download qwen3-1.7b    # 1.4 GB — good balance
foundry model download phi-3.5-mini  # 1.9 GB — strong reasoning
foundry model download phi-4-mini    # 2.2 GB — latest Phi
```

Then update `config.py` and restart the app.

### Q: Can I add support for more file types?

Edit `ALLOWED_EXTENSIONS` in `config.py`:
```python
ALLOWED_EXTENSIONS = {'.md', '.py', '.txt', '.json', '.js', '.ts', '.yaml', '.toml'}
```

### Q: How do I disable Streamlit telemetry?

Create `%userprofile%/.streamlit/config.toml`:
```toml
[browser]
gatherUsageStats = false
```

### Q: Can I index multiple projects at once?

Currently one collection at a time. To index a different project, change the directory and re-index. Previous embeddings are deleted.

### Q: Where are the vector embeddings stored?

In `./chroma_storage/chroma.sqlite3` — a standard SQLite database. You can delete this folder to free space; it will be recreated on next indexing.

### Q: What if Foundry Local is not running?

The app will show an error message telling you to start Foundry Local. Chat will not work without it, but the UI will still load.

### Q: Can I customize the prompt template?

Edit `build_prompt()` in `llm_client.py`. The current template instructs the model to only use provided context and to cite sources.

---

## Troubleshooting

### "Connection Refused" when querying Foundry Local

**Cause**: Foundry Local daemon is not running.

**Fix**:
```bash
foundry server start
foundry model load qwen3-0.6b
foundry model load qwen3-embedding-0.6b
```

### Models not staying loaded after restart

**Cause**: Models must be explicitly loaded into daemon memory after each server restart.

**Fix**: Re-run `foundry model load` commands:
```bash
foundry model load qwen3-0.6b
foundry model load qwen3-embedding-0.6b
```

### "Model is not loaded" error from API

**Cause**: The model was downloaded but not loaded into the running daemon.

**Fix**:
```bash
foundry model load <model-name>
```

### "The openai python package is not installed" error

**Cause**: Missing dependency.

**Fix**:
```bash
pip install openai
```

### Streamlit fails to start

**Cause**: Virtual environment not activated or dependencies missing.

**Fix**:
```bash
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
streamlit run app.py
```

### Unicode/charmap errors on Windows

**Cause**: Windows console uses cp1252 encoding which cannot render emoji.

**Fix**: This is already handled — `sys.stdout.reconfigure(encoding="utf-8")` is set in `scanner.py` and `app.py`. If you still see it, run:
```bash
set PYTHONIOENCODING=utf-8
streamlit run app.py
```

### Indexing is slow

**Cause**: Embedding each chunk requires an API call to Foundry Local.

**Expected speeds**:
- ~20–40 chunks/second on GPU
- ~5–10 chunks/second on CPU
- A project with 500 chunks takes ~15–30 seconds on GPU

### "Permission denied" on chroma_storage/

**Cause**: ChromaDB lock file from a previous crash.

**Fix**: Delete `chroma_storage/` folder and re-index.

### Foundry Local port conflict

**Cause**: Port already in use or configuration issue.

**Fix**:
```bash
# Reset to auto-assigned port
foundry config set port auto --force
foundry server restart

# Or set a specific free port
foundry config set port 9595 --force
foundry server restart
```

---

## Future Roadmap

- [ ] **Streaming responses** — Show tokens as they're generated instead of waiting for full response
- [ ] **Multi-project collections** — Switch between indexed projects without re-scanning
- [ ] **Hybrid search** — Combine semantic search with BM25 keyword search for better code retrieval
- [ ] **Code-aware chunking** — AST-based splitting for Python files (split at function/class boundaries)
- [ ] **File change watching** — Auto-reindex when source files change
- [ ] **Conversation memory** — Maintain context across multiple chat turns
- [ ] **Export chat** — Save conversation + citations as Markdown or PDF
- [ ] **Docker support** — Containerized deployment with Foundry Local bundled

---

## Acknowledgments

This project was developed as part of the **Microsoft AI Innovators Summer Program 2026**.

Built with:
- [Microsoft Foundry Local](https://github.com/microsoft/Foundry-Local) — On-device AI inference platform
- [ChromaDB](https://www.trychroma.com/) — Open-source vector database
- [LangChain](https://www.langchain.com/) — Text splitting utilities
- [Streamlit](https://streamlit.io/) — Python web UI framework
- [Qwen3](https://qwenlm.github.io/) by Alibaba — Open-weight chat and embedding models

---

*Made by **Himmet Can Umutlu** — August 8, 2026*
