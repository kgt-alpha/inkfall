"""
text_processor.py

Why do we need it?
    LLMs and embedding models work best on small, focused pieces of text —
    not entire PDF pages at once. This module splits each page's text into
    smaller overlapping chunks using RecursiveCharacterTextSplitter (smarter
    than the old CharacterTextSplitter because it tries to split on
    paragraphs/sentences first, keeping chunks more coherent).

Input:
    documents -> list of dicts from pdf_reader.py: {"text", "source", "page"}

Output:
    (chunks, metadatas)
    chunks    -> list of strings (the actual text pieces)
    metadatas -> list of dicts (same length as chunks), each: {"source", "page"}
                 metadatas[i] describes where chunks[i] came from

Who calls it?
    app.py, right after extract_text_with_metadata()

How it connects to the next step:
    chunks + metadatas go to vector_store.py, which turns each chunk into an
    embedding and stores it in FAISS, keeping the matching metadata attached.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter


def create_text_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = []
    metadatas = []

    for doc in documents:
        split_texts = text_splitter.split_text(doc["text"])
        for chunk in split_texts:
            chunks.append(chunk)
            metadatas.append({
                "source": doc["source"],
                "page": doc["page"]
            })

    return chunks, metadatas
