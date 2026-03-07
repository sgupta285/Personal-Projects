import argparse

from app.eval.pipeline import EvaluationPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM evaluation pipeline")
    parser.add_argument("--dataset", required=True, help="Path to QA evaluation dataset JSONL")
    parser.add_argument("--retrieval-corpus", required=True, help="Path to retrieval corpus JSONL")
    parser.add_argument("--backend", default="hf-local", choices=["hf-local", "vllm-openai"])
    parser.add_argument("--model", default="sshleifer/tiny-gpt2")
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--experiment-name", default="llm-eval-demo")
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--retrieval-top-k", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = EvaluationPipeline(
        dataset_path=args.dataset,
        retrieval_corpus_path=args.retrieval_corpus,
        backend=args.backend,
        model=args.model,
        base_url=args.base_url,
        experiment_name=args.experiment_name,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        retrieval_top_k=args.retrieval_top_k,
    )
    result = pipeline.run()
    print("Run ID:", result["run_id"])
    print("Metrics:", result["metrics"])
    print("Output path:", result["output_path"])


if __name__ == "__main__":
    main()
