# ============================================================
# app/repositories/repositorio_usuario.py — Acesso a Dados do Usuário
# ============================================================
# Técnica: Repository Pattern.
#
# O repositório recebe uma Session do SQLAlchemy via construtor
# (injeção de dependência manual) e fornece métodos específicos
# para operações com a entidade Usuario.
#
# Vantagens:
#   - Centraliza todas as queries de Usuario em um só lugar.
#   - As camadas superiores (services) não precisam saber SQL.
#   - Mudanças no ORM afetam apenas este arquivo.
# ============================================================

from typing import Optional

from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class RepositorioUsuario:
    """
    Repositório para operações com a entidade Usuario.

    Técnica: Injeção de dependência via construtor.
    A sessão do banco é recebida como parâmetro, permitindo
    que o serviço compartilhe a mesma transação entre
    múltiplos repositórios.
    """

    def __init__(self, db: Session):
        """
        Inicializa o repositório com uma sessão do banco.

        Args:
            db: Sessão SQLAlchemy (injetada pelo dependências).
        """
        self.db = db

    # ----------------------------------------------------------
    # Métodos CRUD Básicos
    # ----------------------------------------------------------

    def salvar(self, usuario: Usuario) -> Usuario:
        """
        Persiste um novo usuário no banco de dados.

        Técnica: SQLAlchemy Session.add + commit/flush.
          - add(): adiciona o objeto à sessão (INSERT pendente).
          - commit(): confirma a transação (executa o INSERT).
          - refresh(): recarrega o objeto do banco (obtém o id gerado).

        Args:
            usuario: Instância de Usuario (sem id, gerado pelo banco).

        Returns:
            Usuario com id populado pelo banco.
        """
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """
        Busca um usuário pelo ID.

        Técnica: Session.query.get().
          get() busca pela chave primária e retorna None se não existir.

        Args:
            usuario_id: ID do usuário a ser buscado.

        Returns:
            Usuario se encontrado, None caso contrário.
        """
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """
        Busca um usuário pelo email.

        Técnica: filter com first().
          filter() adiciona cláusula WHERE.
          first() retorna o primeiro resultado ou None.

        Args:
            email: Email do usuário a ser buscado.

        Returns:
            Usuario se encontrado, None caso contrário.
        """
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def buscar_todos(self) -> list[Usuario]:
        """
        Lista todos os usuários cadastrados.

        Técnica: Session.query.all().
          all() retorna todos os resultados como lista.

        Returns:
            Lista de Usuario (vazia se não houver nenhum).
        """
        return self.db.query(Usuario).all()

    def atualizar(self, usuario: Usuario) -> Usuario:
        """
        Atualiza um usuário existente.

        Técnica: Commit com objeto já attachado.
          Como o objeto foi buscado pela mesma sessão, o
          SQLAlchemy detecta alterações automaticamente e
          gera o UPDATE no commit.

        Args:
            usuario: Instância de Usuario com dados atualizados.

        Returns:
            Usuario atualizado.
        """
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def deletar(self, usuario_id: int) -> None:
        """
        Remove um usuário pelo ID.

        Técnica: delete() com sincronização de sessão.
          synchronize_session="fetch" atualiza a sessão para
          refletir a deleção.

        Args:
            usuario_id: ID do usuário a ser deletado.
        """
        usuario = self.buscar_por_id(usuario_id)
        if usuario:
            self.db.delete(usuario)
            self.db.commit()
