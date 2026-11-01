from fastapi import APIRouter, Depends
from app.api.security import verify_service_token
from app.schemas.recommendation import (
    EvaluationRequest,
    EvaluationResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post(
    "/recommendations/evaluate",
    response_model=EvaluationResponse,
    tags=["recommendations"],
    dependencies=[Depends(verify_service_token)],
)
async def evaluate_recommendations(payload: EvaluationRequest):
    # async: el cálculo es CPU liviano; evita crear hilos del pool.
    return RecommendationService.evaluate(payload)
