from fastapi import APIRouter

from app.models.schemas import AssignmentResponse, ExperimentSummaryRequest
from app.services.runtime import runtime

router = APIRouter()


@router.get("/assignment/{user_id}", response_model=AssignmentResponse)
def get_assignment(user_id: str) -> AssignmentResponse:
    assignment = runtime.ab_testing.get_assignment(user_id)
    return AssignmentResponse(user_id=user_id, **assignment)


@router.post("/summary")
def summary(request: ExperimentSummaryRequest) -> dict:
    return runtime.ab_testing.summary(request.events)
