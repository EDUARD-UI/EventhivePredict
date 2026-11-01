from app.services.scoring import calculate_score, classify_affinity


def test_score_caps_each_behavior():
    result = calculate_score(favorites=50, purchases=50, tickets=50)
    assert result.total == 100
    assert result.favorites == 40
    assert result.purchases == 45
    assert result.tickets == 15


def test_affinity_levels():
    assert classify_affinity(75, 60, 30) == "ALTA"
    assert classify_affinity(45, 60, 30) == "MEDIA"
    assert classify_affinity(20, 60, 30) == "BAJA"


def test_zero_activity():
    assert calculate_score(0, 0, 0).total == 0
