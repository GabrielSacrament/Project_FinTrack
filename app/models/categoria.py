# ============================================================
# app/models/categoria.py — Modelo da Tabela "categorias"
# ============================================================
# Técnica: SQLAlchemy ORM com Mapped (Type Annotations).
#
# As categorias são usadas para classificar receitas e despesas.
# Exemplos: "Alimentação", "Transporte", "Salário", "Lazer".
# ============================================================

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Categoria(Base):
    """
    Modelo SQLAlchemy para a tabela "categorias".

    Técnica: Declarative Mapping.
    Cada instância representa uma linha na tabela categorias.

    Atributos:
        id: Chave primária auto-incrementada.
        nome: Nome da categoria (ex: "Alimentação").
        criado_em: Data/hora de criação.
    """

    # Nome da tabela no banco de dados.
    __tablename__ = "categorias"

    # --- Colunas ---
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Técnica: unique=True garante nomes de categorias únicos.
    nome: Mapped[str] = mapped_column(String(100), unique=True)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Categoria(id={self.id}, nome='{self.nome}')>"
