"""
vector_store.py

Why do we need it?
    To find which chunks are relevant to a user's question, we need to convert
    text into embeddings (numeric vectors that capture meaning), then store
    those vectors somewhere searchable. FAISS is that searchable store — it
    lets us quickly find the chunks whose embeddings are most "similar" to the
    embedding of the user's question.

Input:
    chunks    -> list of text strings (from text_processor.py)
    metadatas -> list of dicts (source/page info), same length as chunks

Output:
    vectorstore -> a FAISS vector store object, ready to be turned into a
                   retriever (i.e. something that can search itself)

Who calls it?
    app.py, right after create_text_chunks()

How it connects to the next step:
    vectorstore goes to chatbot.py, where it's wrapped in a
    ConversationalRetrievalChain together with the Gemini LLM.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


def build_vectorstore(chunks, metadatas):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    vectorstore = FAISS.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas
    )

    return vectorstore
