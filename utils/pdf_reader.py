"""
pdf_reader.py

Why do we need it?
    PDFs are binary files — we can't feed them directly to an LLM. This module
    extracts raw text from each page of each uploaded PDF, and keeps track of
    WHICH file and WHICH page each piece of text came from. That metadata is
    what lets us later show "Sources" under each answer.

Input:
    pdf_docs -> list of uploaded PDF file objects (from Streamlit's file_uploader)

Output:
    (documents, total_pages)
    documents   -> list of dicts: {"text": ..., "source": filename, "page": page_number}
    total_pages -> int, total number of pages across all uploaded PDFs

Who calls it?
    app.py, inside process_documents(), when the user clicks "Build Knowledge Base"

How it connects to the next step:
    The `documents` list goes to text_processor.py, which splits each page's text
    into smaller overlapping chunks (still tagged with source + page).
"""

from PyPDF2 import PdfReader


def extract_text_with_metadata(pdf_docs):
    documents = []
    total_pages = 0

    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        filename = pdf.name

        for page_num, page in enumerate(pdf_reader.pages, start=1):
            total_pages += 1
            page_text = page.extract_text()

            # Some pages (scanned/image-only) return None instead of text.
            # Skipping them avoids crashes and avoids polluting the knowledge base.
            if page_text:
                documents.append({
                    "text": page_text,
                    "source": filename,
                    "page": page_num
                })

    return documents, total_pages
