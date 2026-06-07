# ============================================================
# app/services/servico_categoria.py — Regras de Negócio de Categoria
# ============================================================
# Técnica: Service Layer com regras de unicidade.
# ============================================================

from fastapi import HTTPException, status

from app.models.categoria import Categoria
from app.repositories.repositorio_categoria import RepositorioCategoria
from app.schemas.categoria_schema import (
    AtualizarCategoriaSchema,
    CriarCategoriaSchema,
)


class ServicoCategoria:
    """
    Serviço responsável pelas regras de negócio de categorias.

    Técnica: Mesmo padrão de ServicoUsuario.
    """

    def __init__(self, repositorio: RepositorioCategoria):
        self.repositorio = repositorio

    def criar_categoria(self, dados: CriarCategoriaSchema) -> Categoria:
        """
        Cria uma nova categoria.

        Regra de negócio: nome da categoria deve ser único.
        """
        # Verificar duplicidade
        # Técnica: busca por nome antes de criar.
        categoria_existente = self.repositorio.buscar_por_nome(dados.nome)

        if categoria_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Categoria '{dados.nome}' já existe",
            )

        categoria = Categoria(nome=dados.nome)
        return self.repositorio.salvar(categoria)

    def listar_categorias(self) -> list[Categoria]:
        """
        Lista todas as categorias disponíveis.
        """
        return self.repositorio.buscar_todos()

    def obter_categoria(self, categoria_id: int) -> Categoria:
        """
        Obtém uma categoria pelo ID.
        """
        categoria = self.repositorio.buscar_por_id(categoria_id)

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )

        return categoria

    def atualizar_categoria(
        self, categoria_id: int, dados: AtualizarCategoriaSchema
    ) -> Categoria:
        """
        Atualiza uma categoria existente.
        """
        categoria = self.repositorio.buscar_por_id(categoria_id)

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )

        if dados.nome is not None:
            # Verificar duplicidade do novo nome
            categoria_existente = self.repositorio.buscar_por_nome(dados.nome)
            if categoria_existente and categoria_existente.id != categoria_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Categoria '{dados.nome}' já existe",
                )
            categoria.nome = dados.nome

        return self.repositorio.atualizar(categoria)

    def deletar_categoria(self, categoria_id: int) -> None:
        """
        Remove uma categoria.

        Regra: se houver receitas/despesas vinculadas, o banco
        impede a deleção (ondelete="RESTRICT" no modelo).
        """
        categoria = self.repositorio.buscar_por_id(categoria_id)

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )

        try:
            self.repositorio.deletar(categoria_id)
        except Exception:
            # Captura erros de integridade referencial
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não é possível deletar: existem receitas ou "
                "despesas vinculadas a esta categoria",
            )
