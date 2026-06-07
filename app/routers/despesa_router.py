# ============================================================
# app/routers/despesa_router.py — Endpoints de Despesa
# ============================================================
# Técnica: CRUD com autenticação — estrutura análoga à Receita.
# ============================================================

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import obter_sessao
from app.core.dependencias import obter_usuario_atual
from app.models.usuario import Usuario
from app.repositories.repositorio_categoria import RepositorioCategoria
from app.repositories.repositorio_despesa import RepositorioDespesa
from app.schemas.despesa_schema import (
    AtualizarDespesaSchema,
    CriarDespesaSchema,
    RespostaDespesaSchema,
)
from app.services.servico_despesa import ServicoDespesa

router = APIRouter(
    prefix="/despesas",
    tags=["despesas"],
)


def criar_servico_despesa(db: Session) -> ServicoDespesa:
    repositorio = RepositorioDespesa(db)
    repositorio_categoria = RepositorioCategoria(db)
    return ServicoDespesa(repositorio, repositorio_categoria)


@router.post(
    "/",
    response_model=RespostaDespesaSchema,
    status_code=201,
    summary="Criar nova despesa",
)
def criar_despesa(
    dados: CriarDespesaSchema,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Registra uma nova despesa para o usuário autenticado.
    """
    servico = criar_servico_despesa(db)
    return servico.criar_despesa(dados, usuario_atual.id)


@router.get(
    "/",
    response_model=list[RespostaDespesaSchema],
    summary="Listar despesas",
)
def listar_despesas(
    data_inicio: Optional[date] = Query(
        None, description="Data inicial do filtro"
    ),
    data_fim: Optional[date] = Query(
        None, description="Data final do filtro"
    ),
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Lista as despesas do usuário autenticado.

    Técnica: Query parameters opcionais para filtro.
    """
    servico = criar_servico_despesa(db)
    return servico.listar_despesas(
        usuario_atual.id, data_inicio, data_fim
    )


@router.get(
    "/{despesa_id}",
    response_model=RespostaDespesaSchema,
    summary="Obter despesa por ID",
)
def obter_despesa(
    despesa_id: int,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Obtém uma despesa específica (somente do próprio usuário).
    """
    servico = criar_servico_despesa(db)
    return servico.obter_despesa(despesa_id, usuario_atual.id)


@router.put(
    "/{despesa_id}",
    response_model=RespostaDespesaSchema,
    summary="Atualizar despesa",
)
def atualizar_despesa(
    despesa_id: int,
    dados: AtualizarDespesaSchema,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Atualiza uma despesa (somente do próprio usuário).
    """
    servico = criar_servico_despesa(db)
    return servico.atualizar_despesa(despesa_id, dados, usuario_atual.id)


@router.delete(
    "/{despesa_id}",
    status_code=204,
    summary="Deletar despesa",
)
def deletar_despesa(
    despesa_id: int,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Remove uma despesa (somente do próprio usuário).
    """
    servico = criar_servico_despesa(db)
    servico.deletar_despesa(despesa_id, usuario_atual.id)
