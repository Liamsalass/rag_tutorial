# Env setup:

Go to [https://ollama.com/library/llama3:instruct ](https://ollama.com/download) and download ollama and then both the llama3 model and the nomic-embed-text model.

Using conda, setup the python env using 
```
conda env create -f environment.yml
```
---
# Overview

This script implements a simple Retrieval-Augmented Generation (RAG) loop backed by:
1. A **PostgreSQL** table of past conversations  
2. A **ChromaDB** vector database of embeddings  
3. Calling out to an **Ollama** LLM for both embeddings and chat

You'll be able to:
- Store and fetch chat history from Postgres  
- Build/update a vector store of those conversations  
- Generate “needle-in-the-haystack” queries via the LLM  
- Retrieve the most relevant past exchanges  
- Stream a new LLM response, remembering it for next time  
- Delete the last chat entry on command (`/f`)

---

## Imports and Initialization

- `ollama`: your local LLM interface (chat + embeddings)  
- `chromadb`: the vector database client  
- `psycopg`: PostgreSQL driver  
- `colorama`: for colored console output  
- `tqdm`: progress bars  
- `ast`, `re`: parsing and regexp utilities  

You also define your PostgreSQL credentials in `DB_PARAMS`.

---