# Assignment 2: LLM, Chatbot Architecture and Vector Databases

Written answers to the three Assignment 2 questions, with an architecture diagram and a small runnable vector-search demo.

## Contents

| File | Description |
|---|---|
| `Assignment2_Answers.md` | Full answers: self-rating, LLM chatbot architecture, vector databases and database choice |
| `diagrams/chatbot_architecture.png` | High-level chatbot architecture diagram |
| `demo/toy_vector_search.py` | Toy example of vector search: embeddings, cosine similarity, metadata filtering |
| `demo/make_diagram.py` | Script that generates the architecture diagram |

## Summary of answers

1. **Self-rating:** ML = A, Deep Learning = B, AI = B, LLM = B (see answers file for reasons).
2. **Chatbot architecture:** UI, backend API, orchestrator, prompt management, memory, RAG retrieval (embeddings + vector database), LLM, tools, guardrails, and monitoring.
3. **Vector database:** stores embeddings and finds the most similar by meaning using ANN indexes. For an HR policy chatbot (about 500,000 chunks, filtered search, self-hosted, confidential data) I chose **Qdrant**, and compared it with Pinecone, pgvector, Chroma/FAISS and Milvus.

## Run the demo

```bash
pip install numpy matplotlib
python demo/toy_vector_search.py     # prints ranked search results
python demo/make_diagram.py          # regenerates diagrams/chatbot_architecture.png (run from the demo folder)
```

## Author

Your Name | your.email@example.com | GitHub: your-username
