from dataclasses import dataclass

AFFINITY_HIGH = "ALTA"
AFFINITY_MEDIUM = "MEDIA"
AFFINITY_LOW = "BAJA"


@dataclass(frozen=True)
class ScoreBreakdown:
    favorites: int
    purchases: int
    tickets: int
    total: int


def calculate_score(favorites: int, purchases: int, tickets: int) -> ScoreBreakdown:
    # Los topes evitan que una sola métrica domine indefinidamente el resultado.
    favorite_points = min(favorites, 5) * 8       # Máximo: 40
    purchase_points = min(purchases, 5) * 9      # Máximo: 45
    ticket_points = min(tickets, 15)             # Máximo: 15

    return ScoreBreakdown(
        favorites=favorite_points,
        purchases=purchase_points,
        tickets=ticket_points,
        total=min(100, favorite_points + purchase_points + ticket_points),
    )


def classify_affinity(score: int, high_threshold: int, medium_threshold: int) -> str:
    if score >= high_threshold:
        return AFFINITY_HIGH
    if score >= medium_threshold:
        return AFFINITY_MEDIUM
    return AFFINITY_LOW
