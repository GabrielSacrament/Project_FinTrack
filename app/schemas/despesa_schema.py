# ============================================================
# app/schemas/despesa_schema.py — Schemas de Despesa
# ============================================================
# Técnica: Pydantic v2 — estrutura análoga à Receita.
# ============================================================

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CriarDespesaSchema(BaseModel):
    """
    Schema para criar uma nova despesa.

    Técnica: mesma estrutura de CriarReceitaSchema.
    Poderíamos usar herança, mas a duplicação é intencional
    para facilitar evoluções independentes no futuro.
    """

    descricao: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="Conta de Luz",
    )

    valor: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        example=150.00,
    )

    data: date = Field(
        ...,
        description="Data do pagamento",
        example="2026-01-10",
    )

    categoria_id: int = Field(
        ...,
        gt=0,
        description="ID da categoria",
        example=2,
    )


class AtualizarDespesaSchema(BaseModel):
    """
    Schema para atualizar uma despesa.
    """

    descricao: Optional[str] = Field(
        None, min_length=1, max_length=255, example="Conta de Luz (Ajustada)"
    )
    valor: Optional[Decimal] = Field(None, gt=0, decimal_places=2, example=180.00)
    data: Optional[date] = Field(None, example="2026-01-15")
    categoria_id: Optional[int] = Field(None, gt=0, example=2)


class RespostaDespesaSchema(BaseModel):
    """
    Schema de resposta para despesa.
    """

    id: int
    descricao: str
    valor: Decimal
    data: date
    categoria_id: int
    usuario_id: int
    criado_em: datetime

    model_config = {"from_attributes": True}
