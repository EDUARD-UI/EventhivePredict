from app.schemas.recommendation import RecommendationResult
from app.services.scoring import AFFINITY_HIGH


def select_recipients(
    results: list[RecommendationResult],
    limit: int,
    required_level: str = AFFINITY_HIGH,
) -> list[RecommendationResult]:
    """Devuelve los mejores usuarios para notificar.

    Orden de operaciones (importante):
    1. Filtrar por nivel de afinidad requerido.
    2. Ordenar por puntuación descendente (desempate por usuario_id).
    3. Recién entonces aplicar el límite.
    """
    eligible = [item for item in results if item.afinidad == required_level]
    eligible.sort(key=lambda item: (-item.puntuacion, item.usuario_id))
    return eligible[:limit]
