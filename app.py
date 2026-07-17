"""
app.py

Why do we need it?
    This is the entry point of Inkfall — the Streamlit UI. It ties
    together all four utils modules: reading PDFs, chunking text, building
    the vector store, and running the conversation chain. It also owns all
    the UI polish from the checklist: header, sidebar upload, progress bar,
    stats, and a ChatGPT-like chat interface with source citations.

Input:
    User interactions via the Streamlit UI (PDF uploads, button clicks,
    chat messages). No function-call input — this is the app runner.

Output:
    Renders the full Inkfall web app in the browser.

Who calls it?
    Run directly: `streamlit run app.py`

How it connects to the previous steps:
    process_documents() calls, in order:
    extract_text_with_metadata() -> create_text_chunks() -> build_vectorstore()
    -> get_conversation_chain()
    The resulting chain is stored in st.session_state and reused for every
    chat message the user sends afterward.
"""

import streamlit as st
from dotenv import load_dotenv

from utils.pdf_reader import extract_text_with_metadata
from utils.text_processor import create_text_chunks
from utils.vector_store import build_vectorstore
from utils.chatbot import get_conversation_chain


def init_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "stats" not in st.session_state:
        st.session_state.stats = None


def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ---- App shell with layered texture ---- */
        .stApp {
            background-color: #12141A;
            background-image:
                radial-gradient(circle at 12% 8%, rgba(79, 209, 197, 0.08), transparent 38%),
                radial-gradient(circle at 88% 92%, rgba(217, 166, 87, 0.06), transparent 42%),
                repeating-linear-gradient(135deg, rgba(255,255,255,0.012) 0px, rgba(255,255,255,0.012) 1px, transparent 1px, transparent 4px);
            color: #ECE8DD;
        }

        [data-testid="stHeader"] {
            background: transparent;
            border-bottom: 1px solid #262A35;
        }

        [data-testid="stToolbar"] * {
            color: #8890A0 !important;
        }

        .block-container {
            padding-top: 2rem;
        }

        /* ---- Default text colors ---- */
        .stApp, .stApp p, .stApp span, .stApp label,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
            color: #ECE8DD;
        }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {
            background: #181B23;
            border-right: 1px solid #262A35;
            box-shadow: inset -12px 0 24px -20px rgba(79, 209, 197, 0.15);
        }

        section[data-testid="stSidebar"] * {
            color: #ECE8DD !important;
        }

        section[data-testid="stSidebar"] .stButton button {
            background: #4FD1C5;
            color: #12141A !important;
            border: none;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.15s ease;
        }

        section[data-testid="stSidebar"] .stButton button:hover {
            background: #3FBDB0;
            transform: translateY(-1px);
        }

        section[data-testid="stSidebar"] .stButton button p {
            color: #12141A !important;
        }

        /* ---- File uploader — broad selectors to survive Streamlit version drift ---- */
        div[data-testid="stFileUploader"] section,
        div[data-testid="stFileUploaderDropzone"],
        div[data-testid="stFileUploader"] > section > div {
            background: #1F232D !important;
            border: 1.5px dashed #3A4150 !important;
            border-radius: 10px !important;
        }

        div[data-testid="stFileUploader"] section:hover {
            border-color: #4FD1C5 !important;
        }

        div[data-testid="stFileUploader"] * {
            color: #ECE8DD !important;
        }

        div[data-testid="stFileUploader"] small {
            color: #8890A0 !important;
        }

        div[data-testid="stFileUploader"] button {
            background: #262A35 !important;
            color: #ECE8DD !important;
            border: 1px solid #3A4150 !important;
            border-radius: 6px !important;
        }

        div[data-testid="stFileUploader"] svg {
            fill: #4FD1C5 !important;
        }

        /* ---- Metrics ---- */
        [data-testid="stMetricValue"] {
            color: #4FD1C5 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #8890A0 !important;
        }

        /* ---- Chat messages ---- */
        [data-testid="stChatMessage"] {
            background: #181B23;
            border: 1px solid #262A35;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        }

        [data-testid="stChatMessage"] * {
            color: #ECE8DD;
        }

        /* ---- Chat input ---- */
        [data-testid="stChatInput"] {
            background: #181B23 !important;
            border: 1px solid #262A35 !important;
            border-radius: 12px;
        }

        [data-testid="stChatInput"] textarea {
            background: transparent !important;
            color: #ECE8DD !important;
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: #6B7280 !important;
        }

        [data-testid="stBottomBlockContainer"] {
            background: linear-gradient(180deg, transparent, #12141A 40%);
        }

        /* ---- Expander (Sources) ---- */
        .streamlit-expanderHeader {
            color: #D9A657 !important;
            background: #181B23 !important;
            border: 1px solid #262A35;
            border-radius: 8px;
        }

        .streamlit-expanderContent {
            background: #14161D !important;
            color: #ECE8DD !important;
            border: 1px solid #262A35;
            border-top: none;
        }

        /* ---- Divider ---- */
        hr {
            border-color: #262A35 !important;
        }

        /* ---- Ink drop signature ---- */
        .ink-drop-wrap {
            display: flex;
            justify-content: center;
            height: 22px;
        }

        .ink-drop {
            width: 12px;
            height: 12px;
            background: #4FD1C5;
            border-radius: 50% 50% 50% 0;
            transform: rotate(45deg);
            animation: drip 2.4s ease-in-out infinite;
            box-shadow: 0 0 14px rgba(79, 209, 197, 0.7);
        }

        @keyframes drip {
            0%   { transform: translateY(-4px) rotate(45deg); opacity: 0; }
            30%  { opacity: 1; }
            55%  { transform: translateY(12px) rotate(45deg); opacity: 1; }
            65%  { transform: translateY(12px) rotate(45deg); opacity: 0; }
            100% { transform: translateY(-4px) rotate(45deg); opacity: 0; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    st.set_page_config(page_title="Inkfall", page_icon="📖", layout="wide")
    inject_custom_css()
    st.markdown(
        """
        <div style="text-align:center; padding: 6px 0 25px 0;">
            <div class="ink-drop-wrap"><div class="ink-drop"></div></div>
            <h1 style="font-family: 'Fraunces', serif; font-weight: 600;
                       font-size: 2.6rem; margin: 6px 0 0 0; letter-spacing: -0.5px;
                       color: #ECE8DD;">
                Inkfall
            </h1>
            <p style="color: #9AA2B1; font-size: 1.02rem; margin-top: 8px;">
                When knowledge falls into place — upload your documents and chat with them.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_sidebar():
    with st.sidebar:
        st.subheader("📂 Upload Documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here",
            accept_multiple_files=True,
            type=["pdf"]
        )

        if st.button("🚀 Build Knowledge Base", use_container_width=True):
            if not pdf_docs:
                st.warning("Please upload at least one PDF first.")
            else:
                process_documents(pdf_docs)

        if st.session_state.stats:
            st.divider()
            st.subheader("📊 Stats")
            stats = st.session_state.stats
            col1, col2, col3 = st.columns(3)
            col1.metric("PDFs", stats["num_pdfs"])
            col2.metric("Pages", stats["total_pages"])
            col3.metric("Chunks", stats["total_chunks"])


def process_documents(pdf_docs):
    progress = st.progress(0, text="Reading PDFs...")

    documents, total_pages = extract_text_with_metadata(pdf_docs)
    progress.progress(30, text="Splitting text into chunks...")

    chunks, metadatas = create_text_chunks(documents)
    progress.progress(60, text="Creating embeddings with Gemini...")

    vectorstore = build_vectorstore(chunks, metadatas)
    progress.progress(90, text="Setting up conversation chain...")

    st.session_state.conversation = get_conversation_chain(vectorstore)
    st.session_state.chat_history = []
    st.session_state.stats = {
        "num_pdfs": len(pdf_docs),
        "total_pages": total_pages,
        "total_chunks": len(chunks)
    }

    progress.progress(100, text="Done!")
    st.success(f"✅ Knowledge base built from {len(pdf_docs)} PDF(s)!")


def render_chat():
    # Re-render past messages so they persist across Streamlit reruns
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input("Ask a question about your documents...")

    if user_question:
        if st.session_state.conversation is None:
            st.warning("Please upload and process documents first (see sidebar).")
            return

        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.conversation({"question": user_question})
                answer = response["answer"]
                sources = response.get("source_documents", [])

                st.markdown(answer)

                if sources:
                    with st.expander("📖 Sources"):
                        seen = set()
                        for doc in sources:
                            src = doc.metadata.get("source", "Unknown")
                            page = doc.metadata.get("page", "?")
                            key = f"{src}-{page}"
                            if key not in seen:
                                st.markdown(f"- **{src}**, page {page}")
                                seen.add(key)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})


def main():
    load_dotenv()
    init_session_state()
    render_header()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()