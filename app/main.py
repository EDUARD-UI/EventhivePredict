from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings
from app.core.limits import BodySizeLimitMiddleware

app = FastAPI(
    title="EventHive Predictive Recommendations",
    description="Servicio heurístico de afinidad de eventos para EventHive.",
    version="1.0.0",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

app.add_middleware(BodySizeLimitMiddleware, max_bytes=settings.max_body_bytes)
app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "eventhive-recommendations"}
