# ============================================================
# app/routers/usuario_router.py — Endpoints de Usuário
# ============================================================
# Técnica: FastAPI APIRouter.
#
# O APIRouter permite organizar endpoints em grupos modulares.
# Cada grupo tem seu prefixo e tags (para documentação).
#
# Endpoints:
#   POST /usuarios/          → Criar conta (público)
#   POST /usuarios/login     → Login (público)
#   GET  /usuarios/me        → Perfil (autenticado)
#   PUT  /usuarios/me        → Atualizar perfil (autenticado)
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import obter_sessao
from app.core.dependencias import obter_usuario_atual
from app.models.usuario import Usuario
from app.repositories.repositorio_usuario import RepositorioUsuario
from app.schemas.usuario_schema import (
    AtualizarUsuarioSchema,
    CriarUsuarioSchema,
    LoginSchema,
    RespostaUsuarioSchema,
    TokenSchema,
)
from app.services.servico_usuario import ServicoUsuario

# --- Criação do Router ---
# Técnica: APIRouter com prefixo e tags.
# prefix="/usuarios": todas as rotas começam com /usuarios.
# tags=["usuarios"]: agrupa na documentação Swagger.
router = APIRouter(prefix="/usuarios", tags=["usuarios"])


# --- Factory para o Serviço ---
# Técnica: Função auxiliar para evitar repetição.
# Cria o serviço com suas dependências (repositório).
def criar_servico_usuario(db: Session) -> ServicoUsuario:
    """
    Cria uma instância de ServicoUsuario com as dependências
    necessárias. Centraliza a criação para evitar duplicação.
    """
    repositorio = RepositorioUsuario(db)
    return ServicoUsuario(repositorio)


# ============================================================
# POST /usuarios/
# Criar nova conta (público — não requer autenticação)
# ============================================================
@router.post(
    "/",
    response_model=RespostaUsuarioSchema,
    status_code=201,
    summary="Criar nova conta",
)
def criar_usuario(
    dados: CriarUsuarioSchema,
    db: Session = Depends(obter_sessao),
):
    """
    Cria uma nova conta de usuário.

    Técnica: Endpoint público (sem autenticação).
    O schema CriarUsuarioSchema valida os dados recebidos.

    Args:
        dados: Dados do usuário validados pelo Pydantic.

    Returns:
        RespostaUsuarioSchema (sem senha_hash).
    """
    servico = criar_servico_usuario(db)
    usuario = servico.criar_conta(dados)
    return usuario


# ============================================================
# POST /usuarios/login
# Autenticar usuário e retornar token JWT (público)
# ============================================================
@router.post(
    "/login",
    response_model=TokenSchema,
    summary="Autenticar usuário",
)
def login(
    dados: LoginSchema,
    db: Session = Depends(obter_sessao),
):
    """
    Autentica o usuário e retorna um token JWT.

    Técnica: Login público que retorna token Bearer.
    O token deve ser enviado no header Authorization
    das próximas requisições autenticadas.
    """
    servico = criar_servico_usuario(db)
    return servico.autenticar(dados)


# ============================================================
# GET /usuarios/me
# Obter perfil do usuário autenticado
# ============================================================
@router.get(
    "/me",
    response_model=RespostaUsuarioSchema,
    summary="Obter perfil do usuário",
)
def obter_perfil(
    usuario_atual: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(obter_sessao),
):
    """
    Retorna os dados do perfil do usuário autenticado.

    Técnica: Rota protegida.
    O parâmetro usuario_atual é injetado pela dependência
    obter_usuario_atual, que extrai e valida o token JWT.
    """
    servico = criar_servico_usuario(db)
    return servico.obter_perfil(usuario_atual.id)


# ============================================================
# PUT /usuarios/me
# Atualizar perfil do usuário autenticado
# ============================================================
@router.put(
    "/me",
    response_model=RespostaUsuarioSchema,
    summary="Atualizar perfil",
)
def atualizar_perfil(
    dados: AtualizarUsuarioSchema,
    usuario_atual: Usuario = Depends(obter_usuario_atual),
    db: Session = Depends(obter_sessao),
):
    """
    Atualiza os dados do perfil do usuário autenticado.

    Técnica: Atualização parcial.
    Campos não fornecidos permanecem inalterados.
    """
    servico = criar_servico_usuario(db)
    return servico.atualizar_perfil(usuario_atual.id, dados)
