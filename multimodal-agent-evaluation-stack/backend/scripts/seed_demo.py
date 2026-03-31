from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.analysis import classify_failure
from app.benchmarks import load_default_benchmarks
from app.db import Base, SessionLocal, engine
from app.evaluators import dispatch_evaluator
from app.models import Evaluation, FailureAnalysis, Run
from app.runner import generate_demo_run


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        benchmarks = load_default_benchmarks(db, str(ROOT.parent / "benchmarks"))
        for benchmark in benchmarks:
            modes = ["success", "failure"] if benchmark.evaluator_type == "exact_match" else ["rubric"]
            for mode in modes:
                run_payload = generate_demo_run(benchmark.benchmark_id, mode=mode)
                run = Run(**run_payload)
                db.add(run)
                db.commit()
                db.refresh(run)

                result = dispatch_evaluator(
                    evaluator_type=benchmark.evaluator_type,
                    expected_output=benchmark.expected_output,
                    expected_tools=benchmark.expected_tools,
                    actual_output=run.final_output,
                    trajectory=run.trajectory,
                )
                evaluation = Evaluation(
                    evaluation_id=f"eval-{run.run_id}",
                    run_id=run.run_id,
                    benchmark_id=run.benchmark_id,
                    evaluator_type=benchmark.evaluator_type,
                    score=result.score,
                    success=result.success,
                    metrics=result.metrics,
                )
                db.add(evaluation)
                db.commit()

                failure = classify_failure(run_payload, {"success": result.success})
                analysis = FailureAnalysis(
                    analysis_id=f"fa-{run.run_id}",
                    run_id=run.run_id,
                    benchmark_id=run.benchmark_id,
                    failure_mode=failure.failure_mode,
                    rationale=failure.rationale,
                    signals=failure.signals,
                )
                db.add(analysis)
                db.commit()

        print("Seeded demo benchmarks, runs, evaluations, and failure analyses.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
