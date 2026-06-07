# ============================================================
# app/services/servico_receita.py — Regras de Negócio de Receita
# ============================================================
# Técnica: Service Layer com validação de vínculos.
# ============================================================

from datetime import date

from fastapi import HTTPException, status

from app.models.receita import Receita
from app.repositories.repositorio_categoria import RepositorioCategoria
from app.repositories.repositorio_receita import RepositorioReceita
from app.schemas.receita_schema import (
    AtualizarReceitaSchema,
    CriarReceitaSchema,
)


class ServicoReceita:
    """
    Serviço responsável pelas regras de negócio de receitas.
    """

    def __init__(
        self,
        repositorio: RepositorioReceita,
        repositorio_categoria: RepositorioCategoria,
    ):
        """
        Técnica: Múltiplos repositórios.
        O serviço pode usar mais de um repositório quando
        precisa validar dados em outras tabelas.
        """
        self.repositorio = repositorio
        self.repositorio_categoria = repositorio_categoria

    def criar_receita(
        self, dados: CriarReceitaSchema, usuario_id: int
    ) -> Receita:
        """
        Cria uma nova receita para o usuário autenticado.

        Regras:
          1. A categoria deve existir no banco.
          2. A receita é vinculada ao usuário autenticado.
        """
        # Regra 1: Validar categoria
        # Técnica: garante integridade referencial via aplicação.
        categoria = self.repositorio_categoria.buscar_por_id(
            dados.categoria_id
        )
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )

        receita = Receita(
            descricao=dados.descricao,
            valor=dados.valor,
            data=dados.data,
            categoria_id=dados.categoria_id,
            usuario_id=usuario_id,
        )

        return self.repositorio.salvar(receita)

    def listar_receitas(
        self,
        usuario_id: int,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> list[Receita]:
        """
        Lista receitas do usuário com filtro opcional por período.

        Técnica: Parâmetros opcionais para filtros.
        Se datas não forem fornecidas, retorna todas as receitas.
        """
        if data_inicio and data_fim:
            return self.repositorio.buscar_por_periodo(
                usuario_id, data_inicio, data_fim
            )
        return self.repositorio.buscar_por_usuario(usuario_id)

    def obter_receita(self, receita_id: int, usuario_id: int) -> Receita:
        """
        Obtém uma receita verificando se pertence ao usuário.

        Técnica: Validação de propriedade.
        Impede que um usuário veja receitas de outro.
        """
        receita = self.repositorio.buscar_por_id(receita_id)

        if not receita:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receita não encontrada",
            )

        if receita.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar esta receita",
            )

        return receita

    def atualizar_receita(
        self,
        receita_id: int,
        dados: AtualizarReceitaSchema,
        usuario_id: int,
    ) -> Receita:
        """
        Atualiza uma receita (somente do próprio usuário).
        """
        receita = self.obter_receita(receita_id, usuario_id)

        if dados.descricao is not None:
            receita.descricao = dados.descricao
        if dados.valor is not None:
            receita.valor = dados.valor
        if dados.data is not None:
            receita.data = dados.data
        if dados.categoria_id is not None:
            categoria = self.repositorio_categoria.buscar_por_id(
                dados.categoria_id
            )
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoria não encontrada",
                )
            receita.categoria_id = dados.categoria_id

        return self.repositorio.atualizar(receita)

    def deletar_receita(
        self, receita_id: int, usuario_id: int
    ) -> None:
        """
        Remove uma receita (somente do próprio usuário).
        """
        self.obter_receita(receita_id, usuario_id)
        self.repositorio.deletar(receita_id)
