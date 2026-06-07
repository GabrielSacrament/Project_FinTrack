# ============================================================
# app/schemas/usuario_schema.py — Schemas do Usuário
# ============================================================
# Técnica: Pydantic v2 com validação de dados.
#
# Cada schema representa um "contrato" de dados para uma
# operação específica:
#   - CriarUsuarioSchema: dados necessários para criar conta.
#   - AtualizarUsuarioSchema: dados para atualizar perfil.
#   - RespostaUsuarioSchema: dados retornados pela API (sem senha).
#   - LoginSchema: dados para autenticação.
#   - TokenSchema: resposta do login com token JWT.
#
# Separação de responsabilidades:
#   - Schemas de entrada (request): validam o que o cliente envia.
#   - Schemas de saída (response): controlam o que o cliente vê.
#     Isso evita vazar dados sensíveis (ex: senha_hash).
# ============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# --- Schema de Criação (Input) ---
class CriarUsuarioSchema(BaseModel):
    """
    Schema para criar um novo usuário.

    Técnica: Pydantic BaseModel com validação.
      - nome: validação de tamanho mínimo (3 caracteres).
      - email: usa EmailStr do Pydantic para validar formato de email.
      - senha: validação de tamanho mínimo (6 caracteres).

    EmailStr:
      Valida automaticamente se o email tem formato válido.
      Exige a biblioteca 'email-validator' instalada.
      Ex: "usuario@email.com" ✓  "usuario-invalido" ✗

    Field:
      Permite adicionar metadados e validações extras.
      - min_length: tamanho mínimo da string.
      - examples: exemplo para documentação Swagger.
    """

    # Técnica: Field com validação de tamanho mínimo.
    nome: str = Field(
        ...,  # ... (Ellipsis) = campo obrigatório
        min_length=3,
        max_length=100,
        example="João Silva",
    )

    # Técnica: EmailStr para validação de email.
    email: EmailStr = Field(
        ...,
        example="joao@email.com",
    )

    # Técnica: senha com tamanho mínimo.
    senha: str = Field(
        ...,
        min_length=6,
        max_length=100,
        example="minha-senha-123",
    )


# --- Schema de Atualização (Input) ---
class AtualizarUsuarioSchema(BaseModel):
    """
    Schema para atualizar dados do usuário.

    Técnica: Todos os campos opcionais.
    O usuário pode atualizar apenas um campo por vez.
    Optional[str] = None: campo opcional que pode ser omitido.
    """

    nome: Optional[str] = Field(
        None, min_length=3, max_length=100, example="João Silva Atualizado"
    )
    email: Optional[EmailStr] = Field(None, example="joao.novo@email.com")
    senha: Optional[str] = Field(
        None, min_length=6, max_length=100, example="nova-senha-456"
    )


# --- Schema de Resposta (Output) ---
class RespostaUsuarioSchema(BaseModel):
    """
    Schema para retornar dados do usuário na API.

    Técnica: Schema de saída (não inclui senha_hash).
    Motivo: Princípio do menor privilégio — a API nunca deve
    expor dados sensíveis como hash de senha.

    Configuração: model_config com from_attributes=True.
    Permite criar o schema diretamente de um objeto SQLAlchemy.
    Ex: RespostaUsuarioSchema.model_validate(usuario_obj)
    """

    id: int
    nome: str
    email: str
    criado_em: datetime

    # Técnica: Config interna do Pydantic v2.
    # from_attributes=True (antigo orm_mode no Pydantic v1):
    # permite criar o schema a partir de atributos de objeto
    # (ex: model_validate(usuario)), não apenas de dicionários.
    model_config = {"from_attributes": True}


# --- Schema de Login (Input) ---
class LoginSchema(BaseModel):
    """
    Schema para autenticação (login).

    Recebe email e senha e retorna um token JWT.
    """

    email: EmailStr = Field(..., example="joao@email.com")
    senha: str = Field(..., min_length=6, example="minha-senha-123")


# --- Schema de Token (Output) ---
class TokenSchema(BaseModel):
    """
    Schema para retornar o token JWT após login bem-sucedido.

    Técnica: Schema de resposta para autenticação.
    Retorna o token e o tipo (Bearer) para o cliente usar
    no header Authorization das próximas requisições.
    """

    acesso_token: str = Field(
        ..., description="Token JWT de acesso"
    )
    tipo_token: str = Field(
        default="bearer", description="Tipo do token (sempre Bearer)"
    )
