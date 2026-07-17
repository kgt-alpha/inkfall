# 📖 Inkfall

*When knowledge falls into place.*

Chat with your PDFs — a retrieval-augmented study assistant built with
Streamlit, Google Gemini, LangChain, and FAISS. Upload your documents and
ask questions; every answer is grounded strictly in what you gave it, with
page-level source citations so you always know exactly where the
information came from.

---

## ✨ Features

- Upload multiple PDFs at once
- Automatic text extraction, chunking, and embedding (Gemini)
- Fast semantic search over your documents using FAISS
- ChatGPT-style chat interface with conversation memory (follow-up
  questions work naturally)
- Answers grounded ONLY in your uploaded documents — if the answer isn't
  in there, the assistant says so instead of making things up
- Source citations (filename + page number) shown under each answer
- Live stats: number of PDFs, total pages, total chunks created
- Progress bar + status messages while processing documents

---

## 🏗️ Architecture

```
User uploads PDFs
      │
      ▼
pdf_reader.py        → extracts text per page, tags with (source, page)
      │
      ▼
text_processor.py    → splits text into overlapping chunks (RecursiveCharacterTextSplitter)
      │
      ▼
vector_store.py       → embeds chunks with Gemini, stores in FAISS
      │
      ▼
chatbot.py            → wraps FAISS + Gemini LLM in a ConversationalRetrievalChain
                         with a custom "study assistant" prompt
      │
      ▼
app.py                → Streamlit UI: upload, progress, chat, sources, stats
```

**LLM & Embeddings:** Google Gemini (`gemini-3.5-flash` for chat,
`models/gemini-embedding-001` for embeddings), via `langchain-google-genai`.

---


---

## ⚙️ Installation

1. **Clone this repository** and move into the folder:
   ```bash
   git clone https://github.com/kgt-alpha/inkfall.git
   cd inkfall
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Gemini API key.** Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and add your key:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
   Get a free key at: https://aistudio.google.com/apikey

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

6. Open the URL Streamlit prints (usually `http://localhost:8501`), upload
   PDFs in the sidebar, click **🚀 Build Knowledge Base**, and start chatting.

---

## 📁 Folder Structure

```
inkfall/
│
├── app.py                   # Streamlit UI — entry point
├── utils/
│   ├── __init__.py
│   ├── pdf_reader.py        # Extracts text + metadata from PDFs
│   ├── text_processor.py    # Splits text into chunks
│   ├── vector_store.py      # Builds Gemini embeddings + FAISS store
│   └── chatbot.py           # Gemini LLM + prompt + conversational chain
├── .env.example              # Template for required environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---