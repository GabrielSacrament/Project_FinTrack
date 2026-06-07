# ============================================================
# app/services/servico_usuario.py — Regras de Negócio do Usuário
# ============================================================
# Técnica: Service Layer.
#
# Responsabilidades:
#   - Validar regras de negócio (email único, etc).
#   - Aplicar hash na senha antes de persistir.
#   - Autenticar usuário (login) e gerar token JWT.
#   - Orquestrar repositórios.
#
# O serviço recebe o repositório via construtor (injeção de
# dependência manual), o que permite testar sem banco real.
# ============================================================

from fastapi import HTTPException, status

from app.core.seguranca import (
    criar_token_jwt,
    gerar_hash_senha,
    verificar_senha,
)
from app.models.usuario import Usuario
from app.repositories.repositorio_usuario import RepositorioUsuario
from app.schemas.usuario_schema import (
    AtualizarUsuarioSchema,
    CriarUsuarioSchema,
    LoginSchema,
    TokenSchema,
)


class ServicoUsuario:
    """
    Serviço responsável pelas regras de negócio do usuário.

    Técnica: Injeção de dependência via construtor.
    O repositório é recebido como parâmetro, não instanciado
    internamente. Isso permite:
      1. Trocar o repositório em testes (mock).
      2. Compartilhar a mesma sessão entre serviços.
    """

    def __init__(self, repositorio: RepositorioUsuario):
        """
        Inicializa o serviço com um repositório de usuário.

        Args:
            repositorio: Instância de RepositorioUsuario.
        """
        self.repositorio = repositorio

    # ----------------------------------------------------------
    # Regras de Negócio
    # ----------------------------------------------------------

    def criar_conta(self, dados: CriarUsuarioSchema) -> Usuario:
        """
        Cria uma nova conta de usuário.

        Regras de negócio aplicadas:
          1. Verificar se o email já está cadastrado (deve ser único).
          2. Gerar hash bcrypt da senha (nunca armazenar senha pura).
          3. Persistir o usuário via repositório.

        Técnica: HTTPException para erros de negócio.
        O FastAPI converte automaticamente em respostas HTTP.

        Args:
            dados: Schema validado com nome, email e senha.

        Returns:
            Usuario criado (com id gerado pelo banco).

        Raises:
            HTTPException 400: email já cadastrado.
        """
        # Regra 1: Email único
        # Técnica: busca no banco antes de criar.
        usuario_existente = self.repositorio.buscar_por_email(dados.email)

        if usuario_existente:
            # Técnica: HTTPException com detalhe descritivo.
            # status_code 409 (Conflict) indica conflito com estado atual.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{dados.email}' já está cadastrado",
            )

        # Regra 2: Hash da senha
        # Técnica: bcrypt hash (nunca armazenar senha em texto puro).
        senha_hash = gerar_hash_senha(dados.senha)

        # Cria a instância do modelo ORM
        # Técnica: construtor do SQLAlchemy model.
        usuario = Usuario(
            nome=dados.nome,
            email=dados.email,
            senha_hash=senha_hash,
        )

        # Regra 3: Persistir via repositório
        # Técnica: delegação para o repository.
        return self.repositorio.salvar(usuario)

    def autenticar(self, dados: LoginSchema) -> TokenSchema:
        """
        Autentica o usuário e retorna um token JWT.

        Regras de negócio:
          1. Buscar usuário pelo email.
          2. Verificar se a senha corresponde ao hash armazenado.
          3. Gerar token JWT com os dados do usuário.

        Técnica: Autenticação stateless com JWT.
        Não armazenamos sessão no servidor — o token contém
        tudo que a API precisa saber sobre o usuário.

        Args:
            dados: Schema com email e senha.

        Returns:
            TokenSchema com o token JWT e tipo "bearer".

        Raises:
            HTTPException 401: email ou senha inválidos.
        """
        # Regra 1: Buscar pelo email
        usuario = self.repositorio.buscar_por_email(dados.email)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
            )

        # Regra 2: Verificar senha
        # Técnica: comparação segura com bcrypt.
        if not verificar_senha(dados.senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
            )

        # Regra 3: Gerar token JWT
        # Técnica: payload com dados essenciais.
        # "sub" (subject) = id do usuário (padrão JWT).
        # Incluímos nome para exibição sem nova consulta.
        token = criar_token_jwt({
            "sub": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
        })

        return TokenSchema(acesso_token=token)

    def obter_perfil(self, usuario_id: int) -> Usuario:
        """
        Obtém os dados do perfil do usuário.

        Args:
            usuario_id: ID do usuário autenticado.

        Returns:
            Usuario encontrado.

        Raises:
            HTTPException 404: usuário não encontrado.
        """
        usuario = self.repositorio.buscar_por_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado",
            )

        return usuario

    def atualizar_perfil(
        self, usuario_id: int, dados: AtualizarUsuarioSchema
    ) -> Usuario:
        """
        Atualiza dados do perfil do usuário.

        Técnica: Atualização parcial.
        Só altera campos que foram fornecidos (não None).

        Args:
            usuario_id: ID do usuário a ser atualizado.
            dados: Schema com campos opcionais.

        Returns:
            Usuario atualizado.

        Raises:
            HTTPException 404: usuário não encontrado.
            HTTPException 409: email já em uso por outro usuário.
        """
        usuario = self.repositorio.buscar_por_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado",
            )

        # Atualização parcial: só altera se o campo foi fornecido
        # Técnica: getattr com verificação de None.
        if dados.nome is not None:
            usuario.nome = dados.nome

        if dados.email is not None:
            # Verificar se o novo email já está em uso
            # Técnica: validação de unicidade na atualização.
            usuario_existente = self.repositorio.buscar_por_email(dados.email)
            if usuario_existente and usuario_existente.id != usuario_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{dados.email}' já está em uso",
                )
            usuario.email = dados.email

        if dados.senha is not None:
            usuario.senha_hash = gerar_hash_senha(dados.senha)

        return self.repositorio.atualizar(usuario)
