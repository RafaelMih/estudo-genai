"""Testes para métricas de string."""

import pytest
from modules.evaluation.metrics.string_metrics import rouge_score, bleu_score, exact_match, f1_token_overlap


def test_rouge_identical():
    text = "RAG combina busca vetorial com geração de texto"
    scores = rouge_score(text, text)
    assert scores["rouge1"] == pytest.approx(1.0, abs=1e-3)
    assert scores["rougeL"] == pytest.approx(1.0, abs=1e-3)


def test_rouge_empty():
    scores = rouge_score("", "referência")
    assert all(v == 0.0 for v in scores.values())


def test_bleu_identical():
    text = "RAG é uma técnica de recuperação"
    assert bleu_score(text, text) == pytest.approx(1.0, abs=0.1)


def test_exact_match_true():
    assert exact_match("RAG", "RAG") is True
    assert exact_match("  rag  ", "RAG") is True  # strip + lowercase


def test_exact_match_false():
    assert exact_match("RAG", "LLM") is False


def test_f1_overlap_perfect():
    text = "a b c d e"
    assert f1_token_overlap(text, text) == pytest.approx(1.0, abs=1e-6)


def test_f1_overlap_zero():
    assert f1_token_overlap("abc", "xyz") == pytest.approx(0.0, abs=1e-6)


def test_f1_overlap_partial():
    score = f1_token_overlap("RAG busca documentos", "RAG usa vetores")
    assert 0.0 < score < 1.0
