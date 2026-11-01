from app.schemas.recommendation import RecommendationResult
from app.services.selection import select_recipients


def _r(uid, score, level):
    return RecommendationResult(usuario_id=uid, puntuacion=score, afinidad=level)


def test_limit_is_applied_after_sorting():
    # Llegan desordenados: si se limitara antes de ordenar, se perdería el 99.
    results = [_r(1, 61, "ALTA"), _r(2, 62, "ALTA"), _r(3, 99, "ALTA")]
    chosen = select_recipients(results, limit=2)
    assert [c.usuario_id for c in chosen] == [3, 2]


def test_only_high_affinity_is_selected():
    results = [_r(1, 90, "ALTA"), _r(2, 45, "MEDIA"), _r(3, 10, "BAJA")]
    assert [c.usuario_id for c in select_recipients(results, limit=15)] == [1]


def test_no_high_affinity_means_no_recipients():
    results = [_r(1, 45, "MEDIA"), _r(2, 10, "BAJA")]
    assert select_recipients(results, limit=15) == []


def test_ties_are_deterministic():
    results = [_r(9, 70, "ALTA"), _r(4, 70, "ALTA")]
    assert [c.usuario_id for c in select_recipients(results, limit=15)] == [4, 9]
