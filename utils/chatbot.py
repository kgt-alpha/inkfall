"""
chatbot.py

Why do we need it?
    This is where the actual "conversation" comes together: it connects the
    Gemini LLM, the FAISS retriever, chat memory (so follow-up questions make
    sense), and a custom prompt that forces the assistant to (a) only answer
    from the uploaded PDFs, (b) admit when it doesn't know, and (c) explain
    things simply — matching the "friendly study assistant" behavior we want.

Input:
    vectorstore -> the FAISS vector store built in vector_store.py

Output:
    conversation_chain -> a callable chain. Calling it with
                          {"question": "..."} returns a dict containing
                          "answer" and "source_documents".

Who calls it?
    app.py, right after build_vectorstore(). The returned chain is stored in
    st.session_state.conversation so it persists across user messages.

How it connects to the next step:
    app.py calls this chain every time the user asks a question in the chat
    input, and reads "answer" + "source_documents" from the result to render
    the reply and the "Sources" section.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

CUSTOM_PROMPT = """You are a friendly study assistant helping a student understand their uploaded documents.

Rules:
- Answer ONLY using the information given in the context below (the uploaded PDFs).
- If the answer is not present in the context, clearly say so instead of guessing.
- Explain things in simple, easy-to-understand language, as if teaching a student.
- Be concise but complete.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Answer:"""


def get_conversation_chain(vectorstore):
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.3)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    prompt = PromptTemplate(
        template=CUSTOM_PROMPT,
        input_variables=["context", "chat_history", "question"]
    )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt}
    )

    return conversation_chain
