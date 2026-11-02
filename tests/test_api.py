import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_service_token(monkeypatch):
    monkeypatch.setattr(settings, "service_token", None)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "eventhive-recommendations"


def test_entrypoint_api_index():
    from api.index import app as vercel_app
    vercel_client = TestClient(vercel_app)
    response = vercel_client.get("/health")
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


def test_auth_with_service_token(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "service_token", "secret-test-token")

    payload = {
        "evento": {"id": 1, "categoriaId": 1},
        "candidatos": [{"usuarioId": 1}],
    }

    # Sin encabezado de autorización
    res_no_auth = client.post("/api/v1/recommendations/evaluate", json=payload)
    assert res_no_auth.status_code == 401

    # Con token incorrecto
    res_bad_auth = client.post(
        "/api/v1/recommendations/evaluate",
        json=payload,
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert res_bad_auth.status_code == 401

    # Con token correcto
    res_valid_auth = client.post(
        "/api/v1/recommendations/evaluate",
        json=payload,
        headers={"Authorization": "Bearer secret-test-token"},
    )
    assert res_valid_auth.status_code == 200


def test_candidate_limits_boundary():
    # Probar exactamente 200 candidatos (límite permitido)
    candidatos_200 = [
        {"usuarioId": i, "favoritosCategoria": 1}
        for i in range(1, 201)
    ]
    res_200 = client.post(
        "/api/v1/recommendations/evaluate",
        json={"evento": {"id": 1}, "candidatos": candidatos_200},
    )
    assert res_200.status_code == 200
    assert len(res_200.json()["recomendaciones"]) == 200

    # Probar 201 candidatos (debe ser rechazado con 422)
    candidatos_201 = [
        {"usuarioId": i, "favoritosCategoria": 1}
        for i in range(1, 202)
    ]
    res_201 = client.post(
        "/api/v1/recommendations/evaluate",
        json={"evento": {"id": 1}, "candidatos": candidatos_201},
    )
    assert res_201.status_code == 422


def test_duplicate_candidates_rejected():
    payload = {
        "evento": {"id": 1},
        "candidatos": [
            {"usuarioId": 5, "favoritosCategoria": 1},
            {"usuarioId": 5, "favoritosCategoria": 2},
        ],
    }
    response = client.post("/api/v1/recommendations/evaluate", json=payload)
    assert response.status_code == 422

