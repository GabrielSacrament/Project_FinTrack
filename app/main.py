# ============================================================
# app/main.py — Ponto de Entrada da Aplicação FastAPI
# ============================================================
# Técnica: FastAPI Application Factory.
#
# O FastAPI é um framework web moderno e rápido para APIs REST.
# Ele utiliza:
#   - Pydantic para validação de dados.
#   - Type hints para documentação automática (OpenAPI/Swagger).
#   - Injeção de dependência nativa.
#
# Este arquivo é o ponto de entrada da aplicação. Para executar:
#   uvicorn app.main:app --reload
#
# Parâmetros:
#   - app.main: módulo Python (app/main.py)
#   - app: variável que contém a instância FastAPI
#   - --reload: recarrega automaticamente ao alterar código (dev)
# ============================================================

from fastapi import FastAPI

from app.core.database import criar_tabelas

# --- Importação dos Routers ---
# Técnica: Organização modular com APIRouter.
# Cada router gerencia um grupo de endpoints relacionados.
# As importações são feitas aqui para registrar as rotas
# na aplicação principal.
from app.routers import usuario_router
from app.routers import categoria_router
from app.routers import receita_router
from app.routers import despesa_router

# --- Criação da Aplicação FastAPI ---
# Técnica: Instância do FastAPI com metadados.
# Os parâmetros title, description e version são usados
# para gerar a documentação automática (Swagger UI).
app = FastAPI(
    title="FinTrack",
    description="API de Controle Financeiro Pessoal",
    version="0.1.0",
)

# --- Evento de Startup ---
# Técnica: FastAPI lifespan events (evento startup).
#
# O decorador @app.on_event("startup") registra uma função
# que será executada QUANDO o servidor iniciar.
# Aqui, criamos as tabelas do banco se não existirem.
#
# ATENÇÃO: Em produção, use migrações (Alembic) em vez de
# criar tabelas automaticamente. O create_all é adequado
# para desenvolvimento/estudos.
@app.on_event("startup")
def inicializar_banco():
    """
    Inicializa o banco de dados criando as tabelas.

    Técnica: Chamada de função utilitária no startup.
    criar_tabelas() percorre todos os modelos que herdam
    de Base e executa CREATE TABLE IF NOT EXISTS.
    """
    criar_tabelas()


# --- Endpoint Raiz (Health Check) ---
# Técnica: Rota simples para verificar se a API está rodando.
# Útil para monitoramento e testes rápidos.
@app.get("/")
def raiz():
    """
    Endpoint de health check.

    Retorna uma mensagem simples confirmando que a API
    está funcionando corretamente.
    """
    return {"mensagem": "FinTrack API rodando!"}


# --- Registro dos Routers ---
# Técnica: app.include_router.
# Cada router é registrado com um prefixo e tags.
# O prefixo define a URL base dos endpoints do router.
# As tags agrupam os endpoints na documentação Swagger.
#
# Exemplo:
#   app.include_router(
#       usuario_router.router,
#       prefix="/usuarios",
#       tags=["usuarios"],
#   )
#
app.include_router(usuario_router.router)
app.include_router(categoria_router.router)
app.include_router(receita_router.router)
app.include_router(despesa_router.router)
