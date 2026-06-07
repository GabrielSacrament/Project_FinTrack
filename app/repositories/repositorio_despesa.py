# ============================================================
# app/repositories/repositorio_despesa.py — Acesso a Dados de Despesa
# ============================================================
# Técnica: Repository Pattern — estrutura análoga à Receita.
# ============================================================

from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.despesa import Despesa


class RepositorioDespesa:
    """
    Repositório para operações com a entidade Despesa.
    """

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, despesa: Despesa) -> Despesa:
        self.db.add(despesa)
        self.db.commit()
        self.db.refresh(despesa)
        return despesa

    def buscar_por_id(self, despesa_id: int) -> Optional[Despesa]:
        return (
            self.db.query(Despesa)
            .filter(Despesa.id == despesa_id)
            .first()
        )

    def buscar_por_usuario(
        self, usuario_id: int, skip: int = 0, limit: int = 100
    ) -> list[Despesa]:
        return (
            self.db.query(Despesa)
            .filter(Despesa.usuario_id == usuario_id)
            .order_by(Despesa.data.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def buscar_por_periodo(
        self, usuario_id: int, data_inicio: date, data_fim: date
    ) -> list[Despesa]:
        return (
            self.db.query(Despesa)
            .filter(
                Despesa.usuario_id == usuario_id,
                Despesa.data >= data_inicio,
                Despesa.data <= data_fim,
            )
            .order_by(Despesa.data.desc())
            .all()
        )

    def buscar_todos(self) -> list[Despesa]:
        return self.db.query(Despesa).order_by(Despesa.data.desc()).all()

    def atualizar(self, despesa: Despesa) -> Despesa:
        self.db.commit()
        self.db.refresh(despesa)
        return despesa

    def deletar(self, despesa_id: int) -> None:
        despesa = self.buscar_por_id(despesa_id)
        if despesa:
            self.db.delete(despesa)
            self.db.commit()
