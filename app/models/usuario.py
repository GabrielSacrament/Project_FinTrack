# ============================================================
# app/models/usuario.py — Modelo da Tabela "usuarios"
# ============================================================
# Técnica: SQLAlchemy ORM com Mapped (Type Annotations).
#
# O SQLAlchemy 2.0 introduziu o estilo "Mapped" com type hints:
#   - Mapped[tipo]: indica que o atributo é uma coluna.
#   - mapped_column(...): configura a coluna (tipo, chave, etc).
#
# Vantagens do estilo 2.0:
#   - Melhor integração com type checkers (mypy, pyright).
#   - Código mais limpo e legível.
#   - Inferência automática de tipos das colunas.
# ============================================================

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Usuario(Base):
    """
    Modelo SQLAlchemy para a tabela "usuarios".

    Técnica: Declarative Mapping.
    Cada atributo de classe com tipo Mapped[] vira uma coluna.

    Atributos:
        id: Chave primária auto-incrementada (Integer).
        nome: Nome completo do usuário (String, máximo 100 caracteres).
        email: Email único para login (String, máximo 100 caracteres, UNIQUE).
        senha_hash: Hash bcrypt da senha (String, máximo 255 caracteres).
        criado_em: Data/hora de criação (DateTime, preenchido automaticamente).

    Relacionamentos:
        receitas: Lista de receitas do usuário (um-para-muitos).
        despesas: Lista de despesas do usuário (um-para-muitos).
    """

    # Nome da tabela no banco de dados SQLite.
    __tablename__ = "usuarios"

    # --- Colunas ---

    # Técnica: Chave primária com auto-incremento.
    # primary_key=True cria a constraint PRIMARY KEY.
    # index=True cria um índice para buscas rápidas por id.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Técnica: String com tamanho máximo.
    # nullable=False (padrão) = coluna NOT NULL.
    nome: Mapped[str] = mapped_column(String(100))

    # Técnica: unique=True = cria constraint UNIQUE.
    # Impede que dois usuários tenham o mesmo email.
    # index=True para busca rápida por email (login).
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True
    )

    # Hash da senha (bcrypt). String(255) é suficiente para o hash.
    senha_hash: Mapped[str] = mapped_column(String(255))

    # Técnica: DateTime com server_default.
    # func.now() usa a função NOW() do SQLite no momento do INSERT.
    # Se quiséssemos usar Python, usaríamos default=datetime.now.
    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        # server_default usa SQL: DEFAULT (CURRENT_TIMESTAMP)
        server_default=func.now(),
        # default usa Python: valor padrão se não fornecido
        default=lambda: datetime.now(timezone.utc),
    )

    # --- Relacionamentos ---
    # Técnica: relationship do SQLAlchemy ORM.
    #
    # Usamos strings ("Receita", "Despesa") em vez de importar
    # as classes diretamente para evitar circular imports.
    # O SQLAlchemy resolve estas referências internamente.
    #
    # "cascade" define o comportamento em operações em cascata:
    #   - "all, delete-orphan": se deletar um usuário, deleta
    #     todas as suas receitas e despesas automaticamente.
    receitas = relationship(
        "Receita", back_populates="usuario", cascade="all, delete-orphan"
    )
    despesas = relationship(
        "Despesa", back_populates="usuario", cascade="all, delete-orphan"
    )

    # --- Representação ---
    def __repr__(self) -> str:
        """
        Representação legível do objeto para debugging.

        Técnica: __repr__ padrão do Python.
        Retorna uma string que mostra os atributos principais.
        """
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}')>"
