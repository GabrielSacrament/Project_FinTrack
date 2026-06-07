# ============================================================
# app/repositories/repositorio_receita.py — Acesso a Dados de Receita
# ============================================================
# Técnica: Repository Pattern com filtros avançados.
# ============================================================

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.receita import Receita


class RepositorioReceita:
    """
    Repositório para operações com a entidade Receita.

    Técnica: Métodos específicos para filtros financeiros.
    """

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, receita: Receita) -> Receita:
        """
        Persiste uma nova receita.
        """
        self.db.add(receita)
        self.db.commit()
        self.db.refresh(receita)
        return receita

    def buscar_por_id(self, receita_id: int) -> Optional[Receita]:
        """
        Busca receita pelo ID.
        """
        return (
            self.db.query(Receita)
            .filter(Receita.id == receita_id)
            .first()
        )

    def buscar_por_usuario(
        self, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> list[Receita]:
        """
        Lista receitas de um usuário com paginação.

        Técnica: Paginação com offset/limit.
          - skip: quantos registros pular (offset).
          - limit: máximo de registros por página.

        Útil para listagens com muitos registros.
        """
        return (
            self.db.query(Receita)
            .filter(Receita.usuario_id == usuario_id)
            .order_by(Receita.data.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def buscar_por_periodo(
        self, usuario_id: int, data_inicio: date, data_fim: date
    ) -> list[Receita]:
        """
        Busca receitas em um intervalo de datas.

        Técnica: Filter com operadores de comparação.
          >= (greater or equal) e <= (less or equal).

        Args:
            usuario_id: ID do usuário.
            data_inicio: Data inicial do filtro.
            data_fim: Data final do filtro.

        Returns:
            Lista de receitas no período, ordenadas por data.
        """
        return (
            self.db.query(Receita)
            .filter(
                Receita.usuario_id == usuario_id,
                Receita.data >= data_inicio,
                Receita.data <= data_fim,
            )
            .order_by(Receita.data.desc())
            .all()
        )

    def buscar_todos(self) -> list[Receita]:
        """
        Lista todas as receitas (admin).
        """
        return self.db.query(Receita).order_by(Receita.data.desc()).all()

    def atualizar(self, receita: Receita) -> Receita:
        """
        Atualiza uma receita existente.
        """
        self.db.commit()
        self.db.refresh(receita)
        return receita

    def deletar(self, receita_id: int) -> None:
        """
        Remove uma receita pelo ID.
        """
        receita = self.buscar_por_id(receita_id)
        if receita:
            self.db.delete(receita)
            self.db.commit()
