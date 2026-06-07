# ============================================================
# app/schemas/categoria_schema.py — Schemas de Categoria
# ============================================================
# Técnica: Pydantic v2 com validação de dados.
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CriarCategoriaSchema(BaseModel):
    """
    Schema para criar uma nova categoria.

    Técnica: validação simples com tamanho mínimo.
    O nome da categoria deve ter pelo menos 2 caracteres.
    """

    nome: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome da categoria (ex: Alimentação)",
        example="Alimentação",
    )


class AtualizarCategoriaSchema(BaseModel):
    """
    Schema para atualizar uma categoria.

    Técnica: campo opcional para permitir PATCH parcial.
    """

    nome: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Novo nome da categoria",
        example="Alimentação e Mercado",
    )


class RespostaCategoriaSchema(BaseModel):
    """
    Schema de resposta para categoria.

    Técnica: from_attributes para conversão automática.
    """

    id: int
    nome: str
    criado_em: datetime

    model_config = {"from_attributes": True}
