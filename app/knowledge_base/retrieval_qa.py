import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# Directory where FAISS index is stored
INDEX_DIR = os.path.join(os.path.dirname(__file__), 'faiss_index')

# Number of top chunks to retrieve
DEFAULT_K = 2


def get_vector_store():
    """
    Loads the FAISS vector store from disk.
    """
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    return vector_store


def get_retriever(k=DEFAULT_K):
    """
    Returns a retriever object for the vector store.
    """
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    return retriever


def get_qa_chain(k=DEFAULT_K, model_name="gpt-4", temperature=0.2):
    """
    Returns a RetrievalQA chain with the specified parameters.
    """
    llm = ChatOpenAI(model_name=model_name, temperature=temperature)
    retriever = get_retriever(k=k)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain


def answer_query(query, k=DEFAULT_K):
    """
    Answers a user query using RetrievalQA chain. Returns a tuple: (answer, sources).
    sources — list of source filenames (books) from which the answer was generated.
    """
    qa_chain = get_qa_chain(k=k)
    result = qa_chain({"query": query})
    answer = result["result"]
    # Extract source filenames from source_documents
    sources = set()
    for doc in result.get("source_documents", []):
        source = doc.metadata.get("source")
        if source:
            sources.add(source)
    return answer, list(sources)

# Example usage:
# answer, sources = answer_query("How can a coach help someone find their core values?", k=2)
# print("Answer:", answer)
# print("Sources:", sources) 