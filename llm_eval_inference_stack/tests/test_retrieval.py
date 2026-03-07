from app.retrieval.index import TfidfRetriever


def test_tfidf_retriever_returns_results() -> None:
    rows = [
        {"doc_id": "doc_1", "text": "Transformers are neural networks for sequence modeling."},
        {"doc_id": "doc_2", "text": "FastAPI is a Python framework for APIs."},
    ]
    retriever = TfidfRetriever(rows)
    results = retriever.search("What is FastAPI?", top_k=1)
    assert len(results) == 1
    assert results[0].doc_id == "doc_2"
