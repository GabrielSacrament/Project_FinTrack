# ============================================================
# app/routers/receita_router.py — Endpoints de Receita
# ============================================================
# Técnica: CRUD com autenticação e filtro por período.
# ============================================================

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import obter_sessao
from app.core.dependencias import obter_usuario_atual
from app.models.usuario import Usuario
from app.repositories.repositorio_categoria import RepositorioCategoria
from app.repositories.repositorio_receita import RepositorioReceita
from app.schemas.receita_schema import (
    AtualizarReceitaSchema,
    CriarReceitaSchema,
    RespostaReceitaSchema,
)
from app.services.servico_receita import ServicoReceita

router = APIRouter(
    prefix="/receitas",
    tags=["receitas"],
)


def criar_servico_receita(db: Session) -> ServicoReceita:
    repositorio = RepositorioReceita(db)
    repositorio_categoria = RepositorioCategoria(db)
    return ServicoReceita(repositorio, repositorio_categoria)


@router.post(
    "/",
    response_model=RespostaReceitaSchema,
    status_code=201,
    summary="Criar nova receita",
)
def criar_receita(
    dados: CriarReceitaSchema,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Registra uma nova receita para o usuário autenticado.
    """
    servico = criar_servico_receita(db)
    return servico.criar_receita(dados, usuario_atual.id)


@router.get(
    "/",
    response_model=list[RespostaReceitaSchema],
    summary="Listar receitas",
)
def listar_receitas(
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
    Lista as receitas do usuário autenticado.

    Técnica: Query parameters opcionais para filtro.
    Uso: /receitas/?data_inicio=2026-01-01&data_fim=2026-01-31
    """
    servico = criar_servico_receita(db)
    return servico.listar_receitas(
        usuario_atual.id, data_inicio, data_fim
    )


@router.get(
    "/{receita_id}",
    response_model=RespostaReceitaSchema,
    summary="Obter receita por ID",
)
def obter_receita(
    receita_id: int,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Obtém uma receita específica (somente do próprio usuário).
    """
    servico = criar_servico_receita(db)
    return servico.obter_receita(receita_id, usuario_atual.id)


@router.put(
    "/{receita_id}",
    response_model=RespostaReceitaSchema,
    summary="Atualizar receita",
)
def atualizar_receita(
    receita_id: int,
    dados: AtualizarReceitaSchema,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Atualiza uma receita (somente do próprio usuário).
    """
    servico = criar_servico_receita(db)
    return servico.atualizar_receita(receita_id, dados, usuario_atual.id)


@router.delete(
    "/{receita_id}",
    status_code=204,
    summary="Deletar receita",
)
def deletar_receita(
    receita_id: int,
    db: Session = Depends(obter_sessao),
    usuario_atual: Usuario = Depends(obter_usuario_atual),
):
    """
    Remove uma receita (somente do próprio usuário).
    """
    servico = criar_servico_receita(db)
    servico.deletar_receita(receita_id, usuario_atual.id)
