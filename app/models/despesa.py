# ============================================================
# app/models/despesa.py — Modelo da Tabela "despesas"
# ============================================================
# Técnica: SQLAlchemy ORM com Chave Estrangeira.
#
# Estrutura idêntica à Receita, mas representa saídas
# financeiras (gastos, contas, compras).
# ============================================================

from datetime import date, datetime, timezone

from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Despesa(Base):
    """
    Modelo SQLAlchemy para a tabela "despesas".

    Técnica: Mesma estrutura de Receita.
    Poderíamos usar herança ou uma tabela genérica, mas para
    fins de aprendizado, manter separado é mais claro e segue
    o princípio KISS (Keep It Simple, Stupid).

    Atributos:
        id: Chave primária auto-incrementada.
        descricao: Descrição da despesa (ex: "Conta de Luz").
        valor: Valor monetário da despesa (Numeric(10,2)).
        data: Data em que a despesa foi paga.
        categoria_id: Chave estrangeira para categorias.
        usuario_id: Chave estrangeira para usuarios.
        criado_em: Data/hora de criação do registro.
    """

    __tablename__ = "despesas"

    # --- Colunas ---
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    descricao: Mapped[str] = mapped_column(String(255))

    # Técnica: Numeric para valores monetários.
    valor: Mapped[float] = mapped_column(Numeric(10, 2))

    data: Mapped[date] = mapped_column(Date)

    # Técnica: ForeignKey com ondelete.
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT")
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE")
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # --- Relacionamentos ---
    categoria = relationship("Categoria", lazy="joined")
    usuario = relationship("Usuario", back_populates="despesas", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<Despesa(id={self.id}, descricao='{self.descricao}', "
            f"valor=R${self.valor})>"
        )
