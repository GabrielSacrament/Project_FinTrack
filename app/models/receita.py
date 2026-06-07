# ============================================================
# app/models/receita.py — Modelo da Tabela "receitas"
# ============================================================
# Técnica: SQLAlchemy ORM com Chave Estrangeira.
#
# Chave estrangeira (ForeignKey) é um conceito fundamental de
# bancos relacionais. Ela:
#   1. Garante integridade referencial (não permite órfãos).
#   2. Cria o vínculo entre duas tabelas.
#   3. Permite joins entre as tabelas.
# ============================================================

from datetime import date, datetime, timezone

from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Receita(Base):
    """
    Modelo SQLAlchemy para a tabela "receitas".

    Técnica: Tabela com chave estrangeira.
    Cada Receita pertence a um Usuario e a uma Categoria.

    Atributos:
        id: Chave primária auto-incrementada.
        descricao: Descrição da receita (ex: "Salário Janeiro").
        valor: Valor monetário da receita (Numeric(10,2)).
        data: Data em que a receita foi recebida.
        categoria_id: Chave estrangeira para a tabela categorias.
        usuario_id: Chave estrangeira para a tabela usuarios.
        criado_em: Data/hora de criação do registro.
    """

    __tablename__ = "receitas"

    # --- Colunas ---
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    descricao: Mapped[str] = mapped_column(String(255))

    # Técnica: Numeric para valores monetários.
    # Numeric(10, 2) = 10 dígitos no total, 2 após a vírgula.
    # Exemplos: 12345678.90 (válido), 1.99 (válido).
    # Motivo: evitar problemas de arredondamento do float.
    valor: Mapped[float] = mapped_column(Numeric(10, 2))

    # Técnica: Date (apenas data, sem hora).
    # Para receitas, geralmente importa apenas o dia.
    data: Mapped[date] = mapped_column(Date)

    # Técnica: Chave Estrangeira (ForeignKey).
    #   - "categorias.id": referencia a coluna id da tabela categorias.
    #   - ondelete="RESTRICT": impede deletar categoria se houver
    #     receitas vinculadas a ela.
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT")
    )

    # Técnica: Outra chave estrangeira.
    #   - "usuarios.id": referencia a coluna id da tabela usuarios.
    #   - ondelete="CASCADE": se o usuário for deletado, todas as
    #     suas receitas também são deletadas automaticamente.
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE")
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # --- Relacionamentos ---
    # Técnica: relationship com back_populates.
    # Cria o vínculo bidirecional entre Receita e Categoria.
    # O atributo "categoria" permite acesso direto ao objeto
    # Categoria a partir de uma Receita.
    #
    # Exemplo:
    #   receita = repositorio.buscar_por_id(1)
    #   print(receita.categoria.nome)  # "Salário"
    #
    # lazy="joined": faz JOIN automático ao buscar a receita.
    # Isso evita o problema N+1 queries, mas pode trazer dados
    # desnecessários. Alternativa: lazy="select" (carregamento
    # sob demanda, que pode causar N+1).
    categoria = relationship("Categoria", lazy="joined")

    # Relacionamento bidirecional com Usuario.
    usuario = relationship("Usuario", back_populates="receitas", lazy="joined")

    def __repr__(self) -> str:
        return (
            f"<Receita(id={self.id}, descricao='{self.descricao}', "
            f"valor=R${self.valor})>"
        )
