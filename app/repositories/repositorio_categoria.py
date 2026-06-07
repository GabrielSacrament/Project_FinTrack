# ============================================================
# app/repositories/repositorio_categoria.py — Acesso a Dados de Categoria
# ============================================================
# Técnica: Repository Pattern.
# Estrutura análoga ao RepositorioUsuario.
# ============================================================

from typing import Optional

from sqlalchemy.orm import Session

from app.models.categoria import Categoria


class RepositorioCategoria:
    """
    Repositório para operações com a entidade Categoria.

    Técnica: Mesmos métodos padronizados dos repositórios.
    """

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, categoria: Categoria) -> Categoria:
        """
        Persiste uma nova categoria.

        Técnica: add + commit + refresh.
        """
        self.db.add(categoria)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def buscar_por_id(self, categoria_id: int) -> Optional[Categoria]:
        """
        Busca categoria pelo ID.
        """
        return (
            self.db.query(Categoria)
            .filter(Categoria.id == categoria_id)
            .first()
        )

    def buscar_por_nome(self, nome: str) -> Optional[Categoria]:
        """
        Busca categoria pelo nome exato.

        Útil para verificar duplicidade antes de criar.
        """
        return (
            self.db.query(Categoria)
            .filter(Categoria.nome == nome)
            .first()
        )

    def buscar_todos(self) -> list[Categoria]:
        """
        Lista todas as categorias ordenadas por nome.
        """
        return self.db.query(Categoria).order_by(Categoria.nome).all()

    def atualizar(self, categoria: Categoria) -> Categoria:
        """
        Atualiza uma categoria existente.
        """
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def deletar(self, categoria_id: int) -> None:
        """
        Remove uma categoria pelo ID.
        """
        categoria = self.buscar_por_id(categoria_id)
        if categoria:
            self.db.delete(categoria)
            self.db.commit()
