# ============================================================
# app/schemas/receita_schema.py — Schemas de Receita
# ============================================================
# Técnica: Pydantic v2 com validação de dados financeiros.
# ============================================================

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CriarReceitaSchema(BaseModel):
    """
    Schema para criar uma nova receita.

    Técnica: Decimal e Date.
      - valor: Decimal(10, 2) para precisão monetária.
      - data: date (apenas data, sem hora).
    """

    descricao: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="Salário Janeiro",
    )

    # Técnica: Decimal para valores financeiros.
    # O Pydantic converte automaticamente float/string para Decimal.
    # gt=0: greater than 0 (valores positivos).
    # decimal_places=2: até 2 casas decimais.
    valor: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        example=5000.00,
    )

    data: date = Field(
        ...,
        description="Data do recebimento",
        example="2026-01-15",
    )

    categoria_id: int = Field(
        ...,
        gt=0,
        description="ID da categoria",
        example=1,
    )


class AtualizarReceitaSchema(BaseModel):
    """
    Schema para atualizar uma receita.

    Técnica: todos os campos opcionais.
    """

    descricao: Optional[str] = Field(
        None, min_length=1, max_length=255, example="Salário Janeiro (Ajustado)"
    )
    valor: Optional[Decimal] = Field(None, gt=0, decimal_places=2, example=5200.00)
    data: Optional[date] = Field(None, example="2026-01-20")
    categoria_id: Optional[int] = Field(None, gt=0, example=1)


class RespostaReceitaSchema(BaseModel):
    """
    Schema de resposta para receita.

    Técnica: inclui nome da categoria para facilitar o frontend.
    """

    id: int
    descricao: str
    valor: Decimal
    data: date
    categoria_id: int
    usuario_id: int
    criado_em: datetime

    model_config = {"from_attributes": True}
