from pathlib import Path

from modules.rag.document_loader import load_directory, load_document


def test_load_document_accepts_string_path():
    doc = load_document("modules/rag/data/sample_docs/genai_concepts.md")

    assert doc["metadata"]["source"] == "genai_concepts.md"
    assert doc["metadata"]["format"] == ".md"
    assert len(doc["text"]) > 0


def test_load_document_accepts_path_object():
    doc = load_document(Path("modules/rag/data/sample_docs/python_glossary.txt"))

    assert doc["metadata"]["source"] == "python_glossary.txt"
    assert doc["metadata"]["format"] == ".txt"
    assert len(doc["text"]) > 0


def test_load_directory_accepts_string_path():
    docs = load_directory("modules/rag/data/sample_docs")

    assert len(docs) >= 1
