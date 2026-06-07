# ============================================================
# app/routers/categoria_router.py — Endpoints de Categoria
# ============================================================
# Técnica: CRUD básico protegido por autenticação.
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import obter_sessao
from app.core.dependencias import obter_usuario_atual
from app.models.usuario import Usuario
from app.repositories.repositorio_categoria import RepositorioCategoria
from app.schemas.categoria_schema import (
    AtualizarCategoriaSchema,
    CriarCategoriaSchema,
    RespostaCategoriaSchema,
)
from app.services.servico_categoria import ServicoCategoria

router = APIRouter(
    prefix="/categorias",
    tags=["categorias"],
)


def criar_servico_categoria(db: Session) -> ServicoCategoria:
    repositorio = RepositorioCategoria(db)
    return ServicoCategoria(repositorio)


@router.post(
    "/",
    response_model=RespostaCategoriaSchema,
    status_code=201,
    summary="Criar nova categoria",
)
def criar_categoria(
    dados: CriarCategoriaSchema,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Cria uma nova categoria.

    Técnica: Rota protegida (requer autenticação).
    """
    servico = criar_servico_categoria(db)
    return servico.criar_categoria(dados)


@router.get(
    "/",
    response_model=list[RespostaCategoriaSchema],
    summary="Listar categorias",
)
def listar_categorias(
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Lista todas as categorias disponíveis.

    Técnica: Rota protegida.
    """
    servico = criar_servico_categoria(db)
    return servico.listar_categorias()


@router.get(
    "/{categoria_id}",
    response_model=RespostaCategoriaSchema,
    summary="Obter categoria por ID",
)
def obter_categoria(
    categoria_id: int,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Obtém uma categoria específica pelo ID.
    """
    servico = criar_servico_categoria(db)
    return servico.obter_categoria(categoria_id)


@router.put(
    "/{categoria_id}",
    response_model=RespostaCategoriaSchema,
    summary="Atualizar categoria",
)
def atualizar_categoria(
    categoria_id: int,
    dados: AtualizarCategoriaSchema,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Atualiza os dados de uma categoria.
    """
    servico = criar_servico_categoria(db)
    return servico.atualizar_categoria(categoria_id, dados)


@router.delete(
    "/{categoria_id}",
    status_code=204,
    summary="Deletar categoria",
)
def deletar_categoria(
    categoria_id: int,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Remove uma categoria do banco de dados.

    Técnica: status_code 204 (No Content).
    Não retorna corpo na resposta.

    Regra: não permite deletar se houver
    receitas/despesas vinculadas.
    """
    servico = criar_servico_categoria(db)
    servico.deletar_categoria(categoria_id)
