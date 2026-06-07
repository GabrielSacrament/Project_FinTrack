# ============================================================
# app/core/dependencias.py — Dependências do FastAPI
# ============================================================
# Técnica: FastAPI Dependency Injection.
#
# O FastAPI possui um sistema poderoso de injeção de dependências.
# Uma "dependência" é uma função que pode ser executada antes
# de uma rota e fornecer dados para ela.
#
# Vantagens:
#   1. Reutilização: mesma função usada em várias rotas.
#   2. Testabilidade: podemos substituir dependências em testes.
#   3. Código limpo: a rota não precisa saber como obter os dados.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import obter_sessao
from app.core.seguranca import decodificar_token_jwt
from app.models.usuario import Usuario
from app.repositories.repositorio_usuario import RepositorioUsuario

# --- Esquema de Segurança HTTP Bearer ---
# Técnica: HTTPBearer do FastAPI.
# Extrai automaticamente o token do header Authorization:
#   Authorization: Bearer <token>
# Se o header estiver ausente ou mal formatado, retorna 403.
#
# O HTTPBearer é uma dependência que pode ser injetada em rotas
# para proteger endpoints que exigem autenticação.
seguranca_bearer = HTTPBearer()


# --- Dependência: Obter Usuário Autenticado ---
# Técnica: Função com Depends aninhados.
#
# Esta função é uma dependência que:
#   1. Extrai o token JWT do header (via HTTPBearer).
#   2. Decodifica o token e valida a assinatura.
#   3. Busca o usuário no banco pelo ID contido no token.
#   4. Retorna o usuário ou levanta HTTPException 401.
#
# Uso em rotas:
#   @router.get("/")
#   def listar(usuario: Usuario = Depends(obter_usuario_atual)):
#       ...
def obter_usuario_atual(
    # HTTPBearer extrai as credenciais do header Authorization.
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca_bearer),
    # obter_sessao fornece a sessão do banco (ver database.py).
    db: Session = Depends(obter_sessao),
) -> Usuario:
    """
    Obtém o usuário autenticado a partir do token JWT.

    Fluxo:
        1. credenciais.credentials contém a string do token.
        2. decodificar_token_jwt valida e extrai o payload.
        3. Do payload, extraímos "sub" (subject = id do usuário).
        4. RepositorioUsuario.buscar_por_id obtém o usuário do banco.
        5. Se não encontrado, retorna 401.

    Técnica: Bearer Token Authentication.
    É o padrão mais usado para APIs REST autenticadas.
    O token é enviado em todo request, sem cookies ou sessão.

    Returns:
        Objeto Usuario do banco de dados.

    Raises:
        HTTPException 401: token inválido, expirado ou usuário inexistente.
    """
    # Passo 1: Decodificar o token
    # Se o token for inválido ou expirado, retorna None.
    payload = decodificar_token_jwt(credenciais.credentials)

    if payload is None:
        # Técnica: HTTPException com status code 401 (Unauthorized).
        # O status code 401 indica que o cliente precisa se autenticar.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            # O header WWW-Authenticate indica o esquema de autenticação.
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Passo 2: Extrair o ID do usuário do payload
    # O campo "sub" (subject) é o identificador padrão do JWT.
    usuario_id: int = payload.get("sub")

    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém identificador do usuário",
        )

    # Passo 3: Buscar o usuário no banco de dados
    # Técnica: Repository Pattern para acesso a dados.
    repositorio = RepositorioUsuario(db)
    usuario = repositorio.buscar_por_id(usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )

    # Passo 4: Retornar o usuário autenticado
    # Este objeto ficará disponível como parâmetro na rota.
    return usuario
