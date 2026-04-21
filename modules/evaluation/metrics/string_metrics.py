"""Métricas clássicas de string: ROUGE e BLEU."""

from __future__ import annotations

from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def rouge_score(prediction: str, reference: str, rouge_types: list[str] | None = None) -> dict[str, float]:
    """Calcula ROUGE-1, ROUGE-2 e ROUGE-L entre prediction e reference."""
    rouge_types = rouge_types or ["rouge1", "rouge2", "rougeL"]
    scorer = rouge_scorer.RougeScorer(rouge_types, use_stemmer=False)
    scores = scorer.score(reference, prediction)
    return {k: round(v.fmeasure, 4) for k, v in scores.items()}


def bleu_score(prediction: str, reference: str) -> float:
    """Calcula BLEU entre prediction e reference (tokenização por palavras)."""
    pred_tokens = prediction.lower().split()
    ref_tokens = reference.lower().split()
    smoothing = SmoothingFunction().method1
    score = sentence_bleu([ref_tokens], pred_tokens, smoothing_function=smoothing)
    return round(float(score), 4)


def exact_match(prediction: str, reference: str) -> bool:
    """Match exato após normalização (lowercase, strip)."""
    return prediction.strip().lower() == reference.strip().lower()


def f1_token_overlap(prediction: str, reference: str) -> float:
    """F1 baseado em overlap de tokens (usado em QA)."""
    pred_tokens = set(prediction.lower().split())
    ref_tokens = set(reference.lower().split())
    if not pred_tokens or not ref_tokens:
        return 0.0
    precision = len(pred_tokens & ref_tokens) / len(pred_tokens)
    recall = len(pred_tokens & ref_tokens) / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return round(2 * precision * recall / (precision + recall), 4)


if __name__ == "__main__":
    pred = "RAG combina busca vetorial com geração de texto para melhorar respostas."
    ref = "RAG é uma técnica que usa recuperação de informações para aumentar a qualidade das respostas de LLMs."

    print(f"Prediction: {pred}")
    print(f"Reference:  {ref}\n")
    print(f"ROUGE: {rouge_score(pred, ref)}")
    print(f"BLEU:  {bleu_score(pred, ref)}")
    print(f"F1:    {f1_token_overlap(pred, ref)}")
    print(f"EM:    {exact_match(pred, ref)}")
