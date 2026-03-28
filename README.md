# 🧠 Coding Assistant (RAG + LangChain)

A Coding Assistant built with **Retrieval-Augmented Generation (RAG)** and **LangChain** that retrieves relevant code snippets and documentation to generate accurate, context-aware programming answers with reduced hallucination.

---

## 🚀 Features

* RAG-based context retrieval
* LangChain-powered workflows
* Vector database integration (FAISS/Chroma)
* Accurate, source-grounded responses
* Scalable and modular design

---

## 🛠️ Tech Stack

* Python
* LangChain
* OpenAI / compatible LLMs
* FAISS / Chroma (Vector DB)

---

## ⚙️ Architecture

User Query → Retriever → Vector DB → Context → LLM → Answer

---

## 🔄 How It Works

1. Load documents (code/docs)
2. Convert into embeddings
3. Store in vector database
4. Retrieve relevant chunks
5. Generate answer using LLM

---

## 📦 Installation

git clone <your-repo-url>
cd <your-repo-name>
pip install -r requirements.txt

---

## 🔑 Environment

Create `.env` file:
OPENAI_API_KEY=your_api_key_here

---

## ▶️ Usage

python app.py

Example:
"Explain binary search with code"

---

## 📁 Structure

app.py
requirements.txt
data/
embeddings/
utils/
README.md
---

## 📌 Future Improvements

* Web UI
* Multi-model support
* Better retrieval



Star the repo if helpful ⭐
