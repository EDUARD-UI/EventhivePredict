from app.core.config import settings
from app.schemas.recommendation import (
    EvaluationRequest,
    EvaluationResponse,
    RecommendationResult,
)
from app.services.scoring import calculate_score, classify_affinity
from app.services.selection import select_recipients


class RecommendationService:
    @staticmethod
    def evaluate(payload: EvaluationRequest) -> EvaluationResponse:
        results = []

        for candidate in payload.candidatos:
            score = calculate_score(
                favorites=candidate.favoritos_categoria,
                purchases=candidate.compras_categoria,
                tickets=candidate.entradas_compradas,
            )
            affinity = classify_affinity(
                score.total,
                settings.score_high_threshold,
                settings.score_medium_threshold,
            )
            results.append(
                RecommendationResult(
                    usuario_id=candidate.usuario_id,
                    puntuacion=score.total,
                    afinidad=affinity,
                )
            )

        results.sort(key=lambda item: (-item.puntuacion, item.usuario_id))
        return EvaluationResponse(
            recomendaciones=results,
            destinatarios=select_recipients(results, payload.limite),
        )
