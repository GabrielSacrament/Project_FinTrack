# ============================================================
# app/services/servico_despesa.py — Regras de Negócio de Despesa
# ============================================================
# Técnica: Service Layer — estrutura análoga à Receita.
# ============================================================

from datetime import date

from fastapi import HTTPException, status

from app.models.despesa import Despesa
from app.repositories.repositorio_categoria import RepositorioCategoria
from app.repositories.repositorio_despesa import RepositorioDespesa
from app.schemas.despesa_schema import (
    AtualizarDespesaSchema,
    CriarDespesaSchema,
)


class ServicoDespesa:
    """
    Serviço responsável pelas regras de negócio de despesas.
    """

    def __init__(
        self,
        repositorio: RepositorioDespesa,
        repositorio_categoria: RepositorioCategoria,
    ):
        self.repositorio = repositorio
        self.repositorio_categoria = repositorio_categoria

    def criar_despesa(
        self, dados: CriarDespesaSchema, usuario_id: int
    ) -> Despesa:
        """
        Cria uma nova despesa para o usuário autenticado.
        """
        categoria = self.repositorio_categoria.buscar_por_id(
            dados.categoria_id
        )
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )

        despesa = Despesa(
            descricao=dados.descricao,
            valor=dados.valor,
            data=dados.data,
            categoria_id=dados.categoria_id,
            usuario_id=usuario_id,
        )

        return self.repositorio.salvar(despesa)

    def listar_despesas(
        self,
        usuario_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> list[Despesa]:
        """
        Lista despesas do usuário com filtro opcional por período.
        """
        if data_inicio and data_fim:
            return self.repositorio.buscar_por_periodo(
                usuario_id, data_inicio, data_fim
            )
        return self.repositorio.buscar_por_usuario(usuario_id)

    def obter_despesa(self, despesa_id: int, usuario_id: int) -> Despesa:
        """
        Obtém uma despesa verificando se pertence ao usuário.
        """
        despesa = self.repositorio.buscar_por_id(despesa_id)

        if not despesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Despesa não encontrada",
            )

        if despesa.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar esta despesa",
            )

        return despesa

    def atualizar_despesa(
        self,
        despesa_id: int,
        dados: AtualizarDespesaSchema,
        usuario_id: int,
    ) -> Despesa:
        """
        Atualiza uma despesa (somente do próprio usuário).
        """
        despesa = self.obter_despesa(despesa_id, usuario_id)

        if dados.descricao is not None:
            despesa.descricao = dados.descricao
        if dados.valor is not None:
            despesa.valor = dados.valor
        if dados.data is not None:
            despesa.data = dados.data
        if dados.categoria_id is not None:
            categoria = self.repositorio_categoria.buscar_por_id(
                dados.categoria_id
            )
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoria não encontrada",
                )
            despesa.categoria_id = dados.categoria_id

        return self.repositorio.atualizar(despesa)

    def deletar_despesa(
        self, despesa_id: int, usuario_id: int
    ) -> None:
        """
        Remove uma despesa (somente do próprio usuário).
        """
        self.obter_despesa(despesa_id, usuario_id)
        self.repositorio.deletar(despesa_id)
