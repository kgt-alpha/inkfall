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


def render_header():
    st.set_page_config(page_title="Inkfall", page_icon="📖", layout="wide")
    st.markdown(
        """
        <div style="text-align:center; padding: 10px 0 25px 0;">
            <h1>📖 Inkfall</h1>
            <p style="color: #6b7280; font-size: 1.05rem;">
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