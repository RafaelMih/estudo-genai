"""Avaliação RAGAS-style do pipeline RAG."""

from __future__ import annotations

import json
from pathlib import Path

from modules.evaluation.metrics.llm_judge import LLMJudge
from modules.evaluation.metrics.string_metrics import rouge_score, f1_token_overlap
from modules.evaluation.metrics.semantic_metrics import embedding_similarity
from shared.logger import get_logger

log = get_logger(__name__)

QA_DATASET_PATH = Path("modules/evaluation/datasets/qa_pairs.json")


class RAGEvaluator:
    def __init__(self) -> None:
        self._judge = LLMJudge()

    def evaluate_single(
        self,
        question: str,
        generated_answer: str,
        ground_truth: str,
        contexts: list[str],
    ) -> dict:
        context_str = "\n\n".join(contexts)
        llm_scores = self._judge.evaluate(question, generated_answer, context_str)
        rouge = rouge_score(generated_answer, ground_truth)
        return {
            "question": question,
            "generated_answer": generated_answer[:200],
            "ground_truth": ground_truth[:200],
            "faithfulness": llm_scores.get("faithfulness", 0),
            "relevance": llm_scores.get("relevance", 0),
            "coherence": llm_scores.get("coherence", 0),
            "overall_llm": llm_scores.get("overall", 0),
            "rouge1": rouge.get("rouge1", 0),
            "f1_overlap": f1_token_overlap(generated_answer, ground_truth),
            "semantic_sim": embedding_similarity(generated_answer, ground_truth),
        }

    def evaluate_dataset(self, pipeline) -> list[dict]:
        if not QA_DATASET_PATH.exists():
            log.warning(f"Dataset não encontrado: {QA_DATASET_PATH}")
            return []

        qa_pairs = json.loads(QA_DATASET_PATH.read_text())
        results = []

        for i, pair in enumerate(qa_pairs, 1):
            log.info(f"Avaliando {i}/{len(qa_pairs)}: {pair['question'][:60]}")
            rag_result = pipeline.query(pair["question"])
            contexts = [s["text"] for s in rag_result.get("sources", [])]
            metrics = self.evaluate_single(
                pair["question"],
                rag_result["answer"],
                pair["ground_truth"],
                contexts,
            )
            results.append(metrics)

        return results

    @staticmethod
    def summarize(results: list[dict]) -> dict:
        if not results:
            return {}
        metrics = ["faithfulness", "relevance", "coherence", "overall_llm", "rouge1", "f1_overlap", "semantic_sim"]
        return {m: round(sum(r.get(m, 0) for r in results) / len(results), 3) for m in metrics}
