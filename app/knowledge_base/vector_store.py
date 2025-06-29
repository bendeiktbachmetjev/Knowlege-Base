import os
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# Directory where FAISS index is stored
INDEX_DIR = os.path.join(os.path.dirname(__file__), 'faiss_index')


def load_vector_store():
    """
    Loads the FAISS vector store from disk. Returns a FAISS object ready for retrieval.
    """
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    return vector_store

# Example usage:
# vs = load_vector_store()
# results = vs.similarity_search('What are core values in life coaching?', k=2)
# print(results) 