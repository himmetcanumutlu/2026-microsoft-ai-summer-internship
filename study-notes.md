# Study Notes

These notes summarize the theoretical concepts behind the **Local README & Project Documentation RAG Assistant** project.

---

## What Is RAG?
**RAG (Retrieval-Augmented Generation):** generation augmented by data retrieval. In short, the AI doesn't make things up; it answers by looking things up in the book.

A regular AI model only tells you what it learned during training. A RAG system checks the library first.

- **R – Retrieval:** When you ask a question, the system first scans the documents in its own database and finds the relevant information.
- **A – Augmented:** It attaches the accurate information it found to your question, like a note.
- **G – Generation:** The AI reads these notes and answers based only on the facts in them.

**Pros**
- Accurate information
- Up to date
- Privacy
- Low cost (compared to retraining the model)
- Reliable sources
- Prevents hallucinations
- No need to train a model from scratch

**Cons**
- Slower responses
- Risk of bad data
- Difficult initial setup
- Extra cost: server and search costs
- Language barrier: understanding Turkish documents fully may require a suitable search engine, etc.

---

## Foundry Local
A Microsoft technology that lets you run AI models directly on your own computer instead of in the cloud.

**Pros**
- No internet/cloud costs
- Fully private
- Free
- Uses the device's resources efficiently
- Zero network latency

**Cons**
- Depends on the device's hardware
- Requires a lot of storage
- Limited model capability
- Battery drain
- Difficult initial setup

---

## Project: Local README & Project Documentation Assistant
You scan all the code files in a project (.py, .cs, README.md). Then you ask the AI questions like "How is this project's database connection set up?" or "If I want to add a new API to the project, which class should I copy?"

- **Components:** File Scanner + ChromaDB + Foundry Local
- **UI:** Streamlit or Gradio

---

## File Scanner
Goes to the given file path and walks through the folders recursively (including subfolders). It reads the files it needs and filters out the ones it doesn't. It then splits the files it read into small text chunks and adds metadata.

**Pros**
- Full privacy
- Runs locally
- Flexible filtering
- Clean, noise-free data
- Source tracking

**Cons**
- **Chunking difficulty:** Easy for plain text, but can be a problem for code. Header/AST-based chunking should be used for that.
- **Encoding exceptions:** Non-UTF-8 files can cause problems.
- **Memory load:** Memory usage grows with very large projects.

---

## ChromaDB
An open-source vector database for AI and RAG. Instead of searching for words as they are written, it converts them into lists of numbers (vectors) and searches by meaning. This is called **semantic similarity**.

**Pros**
- Easy setup
- Runs embedded
- Automatic embedding
- Metadata filtering

**Cons**
- Scaling limits
- Version upgrade issues
- Size of the default model

---

## Vector Database: Semantic Similarity
The ability to match words that mean the same thing even when they are written differently.

**Example: searching for "error logs"**
- **Classic database:** Looks only for the exact phrase "error logs". No results. ❌
- **Semantic database:** Searches by meaning and finds results like `error_trace.txt` and "exception reports". ✅
