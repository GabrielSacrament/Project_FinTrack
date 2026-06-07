# ============================================================
# app/core/database.py — Conexão com o Banco de Dados
# ============================================================
# Técnica: SQLAlchemy ORM com Session Local.
#
# O SQLAlchemy é o ORM (Object Relational Mapper) mais usado
# em Python. Ele permite trabalhar com banco de dados usando
# objetos Python ao invés de escrever SQL puro.
#
# Três componentes principais:
#   1. Motor: gerencia a conexão com o banco (pool de conexões).
#   2. SessaoLocal: fábrica de sessões para transações.
#   3. Base: classe base para os modelos (declarative mapping).
#
# Técnica: Declarative Base.
#   Cada modelo SQLAlchemy herda de Base e mapeia uma tabela.
#   O SQLAlchemy lê os atributos da classe e gera o schema
#   automaticamente.
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import config

# --- Motor do Banco ---
# Técnica: create_engine.
# Cria o motor que gerencia o pool de conexões com o SQLite.
# Parâmetros:
#   - config.string_conexao_banco: URL do banco (ex: sqlite:///./fintrack.db).
#   - connect_args={"check_same_thread": False}: necessário para SQLite
#     quando usamos FastAPI (multithread). Permite que a mesma conexão
#     seja compartilhada entre threads diferentes.
#
# Motivo do check_same_thread=False:
#   O SQLite por padrão permite acesso apenas pela thread que criou
#   a conexão. O FastAPI pode usar múltiplas threads, então
#   desabilitamos essa restrição.
motor = create_engine(
    config.string_conexao_banco,
    connect_args={"check_same_thread": False},
)

# --- SessaoLocal (Fábrica de Sessões) ---
# Técnica: sessionmaker.
# Cria uma fábrica que gera sessões do SQLAlchemy.
# Uma sessão representa uma transação com o banco.
# Parâmetros:
#   - autocommit=False: controle manual da transação.
#   - autoflush=False: não envia dados ao banco automaticamente.
#   - bind=motor: associa a sessão ao motor criado acima.
SessaoLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=motor,
)


# --- Base (Classe Base dos Modelos) ---
# Técnica: declarative_base.
# Retorna uma classe base que todos os modelos devem herdar.
# O SQLAlchemy usa essa classe para:
#   1. Mapear classes Python para tabelas do banco.
#   2. Gerar o schema DDL (CREATE TABLE) automaticamente.
#   3. Registrar metadados para criar/alterar tabelas.
Base = declarative_base()


# --- Função para Criar as Tabelas ---
# Técnica: Função utilitária.
# Percorre todos os modelos que herdam de Base e cria as
# tabelas correspondentes no banco, se não existirem.
# Deve ser chamada na inicialização da aplicação.
def criar_tabelas() -> None:
    """
    Cria todas as tabelas definidas nos modelos SQLAlchemy.

    Uso:
        chamada no startup do FastAPI (app/main.py).

    Base.metadata contém o registro de todos os modelos
    que herdam de Base. O método create_all gera as
    instruções CREATE TABLE para cada modelo registrado.
    """
    Base.metadata.create_all(bind=motor)


# --- Dependência do FastAPI (Generator) ---
# Técnica: Generator Function com yield.
#
# O FastAPI suporta dependências que usam yield para
# executar código antes E depois da requisição.
#     - Antes do yield: cria a sessão (setup).
#     - Depois do yield: fecha a sessão (teardown/cleanup).
#
# Isso garante que a sessão seja sempre fechada, mesmo
# se ocorrer uma exceção durante a requisição.
def obter_sessao():
    """
    Generator que fornece uma sessão SQLAlchemy por requisição.

    Fluxo:
        1. Cria uma nova sessão com SessaoLocal().
        2. Entrega a sessão para a rota (via yield).
        3. Após a resposta, fecha a sessão no finally.

    Uso no FastAPI:
        from app.core.database import obter_sessao
        from fastapi import Depends

        @router.get("/")
        def listar(db: Session = Depends(obter_sessao)):
            ...

    Técnica: Dependency Injection (Injeção de Dependência).
    O FastAPI gerencia o ciclo de vida da dependência
    automaticamente.
    """
    db = SessaoLocal()
    try:
        # A palavra-chave 'yield' transforma esta função
        # em um generator. O FastAPI chama next() para
        # obter o valor e executa o finally ao finalizar.
        yield db
    finally:
        # Garantia de que a sessão será fechada mesmo
        # em caso de erro na requisição.
        db.close()
