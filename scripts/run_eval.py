"""CLI: roda a suite de avaliação RAG e salva relatório JSON."""

import argparse
import json
from datetime import datetime
from pathlib import Path

from modules.evaluation.rag_eval import RAGEvaluator
from modules.rag.pipeline import RAGPipeline
from shared.logger import get_logger

log = get_logger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda suite de avaliação RAG")
    parser.add_argument("--output", default="modules/evaluation/reports/eval_run.json", help="Arquivo de saída JSON")
    parser.add_argument("--collection", default="rag_docs", help="Collection ChromaDB a usar")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pipeline = RAGPipeline(collection_name=args.collection)
    evaluator = RAGEvaluator()

    log.info("Iniciando avaliação do pipeline RAG...")
    results = evaluator.evaluate_dataset(pipeline)

    if not results:
        print("Nenhum resultado — verifique se o dataset existe e o ChromaDB está populado.")
        print("Execute: python -m scripts.ingest_docs --dir modules/rag/data/sample_docs")
        return

    summary = evaluator.summarize(results)
    report = {
        "timestamp": datetime.now().isoformat(),
        "collection": args.collection,
        "total_questions": len(results),
        "summary": summary,
        "details": results,
    }

    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    log.info(f"Relatório salvo: {output_path}")

    print("\n=== RESUMO DA AVALIAÇÃO ===")
    for metric, value in summary.items():
        print(f"  {metric:<20} {value}")
    print(f"\nRelatório completo: {output_path}")


if __name__ == "__main__":
    main()
