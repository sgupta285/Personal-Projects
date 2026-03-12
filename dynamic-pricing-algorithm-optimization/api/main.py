from pathlib import Path
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from pricing_engine.schemas import PricingRequest, PricingResponse
from pricing_engine.service import PricingService

app = FastAPI(title="Dynamic Pricing API", version="0.1.0")
service = PricingService.from_artifacts()
ROOT = Path(__file__).resolve().parents[1]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "artifacts_loaded": service.ready, "artifact_dir": str(service.artifact_dir)}


@app.get("/")
def root():
    return {"message": "Dynamic pricing API is running", "dashboard": "/dashboard"}


@app.get("/dashboard")
def dashboard():
    return FileResponse(ROOT / "dashboard/index.html")


@app.get("/dashboard-metrics")
def dashboard_metrics() -> dict:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")
    metrics = json.loads((service.artifact_dir / "metrics.json").read_text())
    return {
        "model_metrics": metrics,
        "backtest_summary": service.backtest_summary,
        "recommendations": service.top_recommendations(limit=50),
        "sample_curve": service.sample_curve.to_dict(orient="records"),
    }


@app.post("/recommend-price", response_model=PricingResponse)
def recommend_price(payload: PricingRequest) -> PricingResponse:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")
    return service.recommend(payload)


@app.get("/top-recommendations")
def top_recommendations(limit: int = Query(25, ge=1, le=200)) -> dict:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")
    return {"recommendations": service.top_recommendations(limit=limit)}


@app.get("/backtest-summary")
def backtest_summary() -> dict:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")
    return service.backtest_summary


@app.get("/sample-sensitivity")
def sample_sensitivity() -> dict:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")
    return service.sample_sensitivity()
