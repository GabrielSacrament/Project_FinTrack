# ============================================================
# app/core/seguranca.py — Hash de Senha e JWT
# ============================================================
# Técnicas:
#   1. bcrypt: algoritmo de hash para senhas.
#      - Hash unidirecional (não pode ser revertido).
#      - Inclui salt automaticamente (protege contra rainbow tables).
#   2. JWT (JSON Web Token): padrão para autenticação stateless.
#      - Token autossuficiente: contém os dados do usuário.
#      - Assinado digitalmente: não pode ser adulterado.
#      - Stateless: o servidor não precisa armazenar sessão.
# ============================================================

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import config

# --- Contexto de Criptografia (Hash de Senha) ---
# Técnica: CryptContext do Passlib.
# O Passlib é a biblioteca padrão para hash de senhas em Python.
# O CryptContext gerencia esquemas de hash (bcrypt, argon, etc).
# Parâmetros:
#   - schemes=["bcrypt"]: usa o algoritmo bcrypt.
#   - deprecated="auto": atualiza esquemas antigos automaticamente.
#
# bcrypt é o recomendado atualmente por ser:
#   - Lento propositalmente (dificulta ataques de força bruta).
#   - Inclui salt aleatório a cada hash.
#   - Amplamente testado e auditado.
contexto_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# Funções de Hash de Senha
# ============================================================


def gerar_hash_senha(senha: str) -> str:
    """
    Gera o hash bcrypt de uma senha em texto puro.

    Técnica: passlib.hash.bcrypt.
    O bcrypt automaticamente:
      1. Gera um salt aleatório (22 caracteres).
      2. Combina salt + senha e aplica o hash.
      3. Retorna uma string no formato:
         $2b$12$<salt><hash>

    Args:
        senha: Senha em texto puro (ex: "minha-senha-123").

    Returns:
        String com o hash no formato bcrypt.
    """
    return contexto_hash.hash(senha)


def verificar_senha(senha_texto: str, senha_hash: str) -> bool:
    """
    Verifica se a senha em texto puro corresponde ao hash armazenado.

    Técnica: passlib.context.verify.
    O método verify extrai o salt do hash armazenado,
    aplica o hash na senha fornecida e compara os resultados.

    Args:
        senha_texto: Senha em texto puro fornecida pelo usuário.
        senha_hash: Hash armazenado no banco de dados.

    Returns:
        True se a senha corresponder ao hash, False caso contrário.
    """
    return contexto_hash.verify(senha_texto, senha_hash)


# ============================================================
# Funções JWT (JSON Web Token)
# ============================================================


def criar_token_jwt(dados: dict) -> str:
    """
    Cria um token JWT com os dados fornecidos.

    Técnica: python-jose (jose = JOSE: JSON Object Signing and Encryption).
    O jwt.encode() recebe:
      1. Payload (dict): os dados que serão codificados no token.
      2. Secret key: chave para assinar o token.
      3. Algorithm: algoritmo de assinatura (HS256).

    Estrutura do JWT:
      Header: {"alg": "HS256", "typ": "JWT"}
      Payload: { "sub": "1", "exp": 1234567890, "nome": "João" }
      Signature: HMAC-SHA256(base64(header) + "." + base64(payload), secret)

    Args:
        dados: Dicionário com os dados do payload
               (ex: {"sub": usuario.id, "nome": usuario.nome}).

    Returns:
        String com o token JWT codificado.
    """
    # Cria uma cópia dos dados para não modificar o original.
    # Técnica: dict expansion (copia rasa).
    payload = {**dados}

    # --- Adiciona a data de expiração ---
    # Técnica: timedelta para calcular a data futura.
    # O campo "exp" (expiration time) é um timestamp UNIX
    # (segundos desde 01/01/1970). O JWT exige esse formato.
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=config.expiracao_token_minutos
    )
    payload["exp"] = expiracao

    # --- Gera o token ---
    # Técnica: jwt.encode do python-jose.
    # Retorna uma string com três partes separadas por pontos:
    #   header.payload.signature
    token = jwt.encode(
        payload,
        config.chave_secreta_jwt,
        algorithm=config.algoritmo_jwt,
    )

    return token


def decodificar_token_jwt(token: str) -> dict | None:
    """
    Decodifica e valida um token JWT.

    Técnica: jwt.decode com tratamento de exceções.
    O decode() automaticamente:
      1. Verifica a assinatura (usando a chave secreta).
      2. Verifica a expiração (campo "exp").
      3. Retorna o payload como dicionário.

    Se o token for inválido ou expirado, retorna None
    em vez de levantar exceção (tratamento seguro).

    Args:
        token: String com o token JWT.

    Returns:
        Dicionário com os dados do payload se válido,
        None se inválido ou expirado.
    """
    try:
        # Técnica: jwt.decode com verificação de expiração.
        # O parâmetro options={"verify_exp": True} é padrão.
        payload = jwt.decode(
            token,
            config.chave_secreta_jwt,
            algorithms=[config.algoritmo_jwt],
        )
        return payload

    except JWTError:
        # Captura qualquer erro JWT:
        # - Token expirado (ExpiredSignatureError)
        # - Assinatura inválida
        # - Mal formatado
        return None
