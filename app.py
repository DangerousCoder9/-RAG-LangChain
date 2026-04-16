from flask import Flask, render_template, request
import boto3
import json

# =========================
# 🔹 RAG CORE IMPORTS
# =========================

# FAISS (facebook ai for similarity search) → Vector database (stores embeddings for fast similarity search)
from langchain_community.vectorstores import FAISS

# Embedding model → converts text into numerical vectors
from langchain_huggingface import HuggingFaceEmbeddings

# Custom function → fetch GitHub issues (our knowledge base)
from github import fetch_github_issues


# =========================
# 🔹 FLASK APP INITIALIZATION
# =========================
app = Flask(__name__)


# =========================
# 🔹 VECTOR DATABASE SETUP
# =========================
def connect_to_vector_store():
    """
    This function creates a vector database.

    Why?
    → LLMs cannot search large text directly
    → We convert text into vectors and store them
    → Then we perform similarity search
    """

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    # This model converts text → numerical vector representation

    # Create FAISS database with initial dummy text
    # (FAISS requires at least one document to initialize)
    return FAISS.from_texts(["init"], embedding=embeddings)


# Initialize vector store
vector_store = connect_to_vector_store()


# =========================
# 🔹 LOAD KNOWLEDGE BASE
# =========================
"""
We fetch real GitHub issues and store them in FAISS.

This becomes our "knowledge source".
This is what makes the system RAG instead of a normal chatbot.
"""
issues = fetch_github_issues("techwithtim", "Flask-Web-App-Tutorial")

# Store issues in vector DB
vector_store.add_documents(issues)


# =========================
# 🔹 RETRIEVER
# =========================
"""
Retriever is responsible for:
→ Taking a query
→ Finding most similar documents

k=5 → return top 5 relevant results
"""
retriever = vector_store.as_retriever(search_kwargs={"k": 5})


# =========================
# 🔹 RETRIEVAL FUNCTION (RAG STEP 1)
# =========================
def search_issues(query):
    """
    Input: user question
    Output: relevant context from GitHub issues

    This is the RETRIEVAL part of RAG
    """

    # Get similar documents based on semantic similarity
    docs = retriever.invoke(query)

    # Combine them into a single context string
    return "\n\n".join([d.page_content[:500] for d in docs]) if docs else "No data"


# =========================
# 🔹 AWS BEDROCK CLIENT
# =========================
"""
This connects our app to AWS foundation models.

Why AWS Bedrock?
→ Managed LLM service
→ No need to host models locally
"""
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


# =========================
# 🔹 LLM FUNCTION (RAG STEP 2)
# =========================
def ask_llm(prompt):
    """
    This function sends prompt to AWS LLM
    and returns generated response.

    This is the GENERATION part of RAG
    """

    # Nova models require "messages" format (chat-style input)
    body = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ]
    })

    # Call AWS model
    response = bedrock.invoke_model(
        modelId="amazon.nova-micro-v1:0",
        body=body
    )

    # Convert response stream → JSON
    result = json.loads(response["body"].read())

    # Extract actual answer text
    output = result["output"]["message"]["content"][0]["text"]

    # =========================
    # 🔹 OUTPUT CLEANING
    # =========================
    """
    LLM sometimes returns markdown or formatting symbols.
    We clean it for better UI display.
    """
    output = output.replace("```", "")
    output = output.replace("###", "")
    output = output.strip()

    return output


# =========================
# 🔹 FLASK ROUTE (UI + BACKEND CONNECT)
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    """
    This is the main route:
    → Handles user input
    → Runs RAG pipeline
    → Returns answer to UI
    """

    answer = None

    if request.method == "POST":
        # Step 1: Get user input from form
        question = request.form.get("question")

        # =========================
        # 🔹 RAG PIPELINE
        # =========================

        # Step 2: Retrieve relevant context
        context = search_issues(question)

        # Step 3: Construct prompt
        """
        Why prompt engineering?
        → Controls LLM output style
        → Prevents messy responses
        """
        prompt = f"""
Answer clearly and concisely.

Rules:
- Keep it simple
- No markdown symbols
- No long explanations
- Use bullet points if helpful

Context:
{context}

Question:
{question}
"""

        # Step 4: Generate answer using LLM
        answer = ask_llm(prompt)

    # Step 5: Render HTML page with answer
    return render_template("index.html", answer=answer)


# =========================
# 🔹 RUN APPLICATION
# =========================
if __name__ == "__main__":
    app.run(debug=True)