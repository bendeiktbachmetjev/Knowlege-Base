from app.services.core.retrieval import AdvancedRetriever

def test_retrieval_basic():
    retriever = AdvancedRetriever(k=1)
    result = retriever.retrieve("What are core values?")
    assert hasattr(result, "chunks")
    assert isinstance(result.chunks, list)
    assert len(result.chunks) > 0
    assert hasattr(result.chunks[0], "text") 