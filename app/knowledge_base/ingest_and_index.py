import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

# Directory with PDF files
PDFS_DIR = os.path.join(os.path.dirname(__file__), 'pdfs')
# Directory to store FAISS index
INDEX_DIR = os.path.join(os.path.dirname(__file__), 'faiss_index')
# Chunk size and overlap for text splitting
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def clean_text(text: str) -> str:
    # Replace tabs with spaces and collapse multiple spaces
    return ' '.join(text.replace('\t', ' ').split())


def ingest_all_pdfs_to_faiss():
    """
    Loads all PDFs from the pdfs directory, splits them into chunks with metadata, embeds them, and saves the FAISS index to disk.
    """
    all_chunks = []
    for filename in os.listdir(PDFS_DIR):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(PDFS_DIR, filename)
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            chunks = splitter.split_documents(documents)
            # Add source metadata to each chunk
            for chunk in chunks:
                if not hasattr(chunk, 'metadata') or chunk.metadata is None:
                    chunk.metadata = {}
                chunk.metadata['source'] = filename
                # Clean text before indexing
                chunk.page_content = clean_text(chunk.page_content)
            all_chunks.extend(chunks)

    if not all_chunks:
        print("No PDF files found in the pdfs directory.")
        return

    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(all_chunks, embedding=embeddings)

    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
    vector_store.save_local(INDEX_DIR)
    print(f"FAISS index saved to {INDEX_DIR} (from {len(all_chunks)} chunks)")


if __name__ == "__main__":
    ingest_all_pdfs_to_faiss() 