from fastapi import FastAPI, HTTPException, Query

from churnintel.schemas import AccountPayload, ExplanationResponse, PredictionResponse
from churnintel.service import ModelService

app = FastAPI(title="Customer Churn Intelligence API", version="0.1.0")
service = ModelService.from_artifacts()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "artifacts_loaded": service.ready,
        "artifact_dir": str(service.artifact_dir),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: AccountPayload) -> PredictionResponse:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")
    return service.predict(payload)


@app.get("/top-risk-accounts")
def top_risk_accounts(limit: int = Query(25, ge=1, le=200), plan_tier: str | None = None) -> dict:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")
    return {"accounts": service.top_risk_accounts(limit=limit, plan_tier=plan_tier)}


@app.get("/intervention-queue")
def intervention_queue(limit: int = Query(25, ge=1, le=200)) -> dict:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")
    return {"accounts": service.intervention_queue(limit=limit)}


@app.get("/account-explanation/{account_id}", response_model=ExplanationResponse)
def account_explanation(account_id: str) -> ExplanationResponse:
    if not service.ready:
        raise HTTPException(status_code=503, detail="Artifacts not found. Run make bootstrap first.")

    explanation = service.explain(account_id)
    if explanation is None:
        raise HTTPException(status_code=404, detail=f"No explanation found for account_id={account_id}")
    return explanation
