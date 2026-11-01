from pydantic import BaseModel, ConfigDict, Field, AliasChoices, model_validator


class EventData(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int
    categoria_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("categoriaId", "categoria_id"),
    )
    categoria_nombre: str | None = Field(
        default=None,
        validation_alias=AliasChoices("categoriaNombre", "categoria_nombre"),
    )


class CandidateData(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    usuario_id: int = Field(
        validation_alias=AliasChoices("usuarioId", "usuario_id")
    )
    favoritos_categoria: int = Field(
        default=0,
        ge=0,
        validation_alias=AliasChoices("favoritosCategoria", "favoritos_categoria"),
    )
    compras_categoria: int = Field(
        default=0,
        ge=0,
        validation_alias=AliasChoices("comprasCategoria", "compras_categoria"),
    )
    entradas_compradas: int = Field(
        default=0,
        ge=0,
        validation_alias=AliasChoices("entradasCompradas", "entradas_compradas"),
    )


class EvaluationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    evento: EventData
    candidatos: list[CandidateData] = Field(default_factory=list)
    limite: int = Field(default=15, ge=1, le=50)

    @model_validator(mode="after")
    def validate_candidate_count(self):
        from app.core.config import settings
        if len(self.candidatos) > settings.max_candidates:
            raise ValueError(
                f"Se permiten como máximo {settings.max_candidates} candidatos."
            )
        ids = [candidate.usuario_id for candidate in self.candidatos]
        if len(ids) != len(set(ids)):
            raise ValueError("La lista contiene usuarios duplicados.")
        return self


class RecommendationResult(BaseModel):
    usuario_id: int = Field(serialization_alias="usuarioId")
    puntuacion: int
    afinidad: str


class EvaluationResponse(BaseModel):
    recomendaciones: list[RecommendationResult]
    destinatarios: list[RecommendationResult]
