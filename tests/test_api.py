from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_evaluate_uses_camel_case_contract():
    response = client.post(
        "/api/v1/recommendations/evaluate",
        json={
            "evento": {"id": 25, "categoriaId": 3, "categoriaNombre": "Música"},
            "candidatos": [
                {
                    "usuarioId": 10,
                    "favoritosCategoria": 5,
                    "comprasCategoria": 3,
                    "entradasCompradas": 4,
                },
                {
                    "usuarioId": 11,
                    "favoritosCategoria": 1,
                    "comprasCategoria": 0,
                    "entradasCompradas": 0,
                },
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()["recomendaciones"]
    assert data[0]["usuarioId"] == 10
    assert data[0]["afinidad"] == "ALTA"
    assert data[1]["afinidad"] == "BAJA"


def test_destinatarios_top15_after_sorting():
    # 30 candidatos ALTA con puntuaciones crecientes, enviados de menor a mayor.
    candidatos = [
        {"usuarioId": i, "favoritosCategoria": 5, "comprasCategoria": 2, "entradasCompradas": i % 15}
        for i in range(1, 31)
    ]
    response = client.post(
        "/api/v1/recommendations/evaluate",
        json={"evento": {"id": 1, "categoriaId": 3}, "candidatos": candidatos},
    )
    body = response.json()
    assert len(body["destinatarios"]) == 15
    scores = [d["puntuacion"] for d in body["destinatarios"]]
    assert scores == sorted(scores, reverse=True)
    assert min(scores) >= max(
        r["puntuacion"] for r in body["recomendaciones"][15:]
    )


def test_oversized_body_is_rejected_with_413():
    big = {"evento": {"id": 1}, "candidatos": [], "relleno": "x" * 200_000}
    response = client.post("/api/v1/recommendations/evaluate", json=big)
    assert response.status_code == 413


def test_openapi_follows_docs_flag():
    from app.core.config import settings
    expected = 200 if settings.docs_enabled else 404
    assert client.get("/openapi.json").status_code == expected
