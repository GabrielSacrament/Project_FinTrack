# ============================================================
# app/routers/__init__.py
# ============================================================
# A pasta 'routers' contém os endpoints da API FastAPI.
#
# Técnica: APIRouter do FastAPI.
# Cada arquivo define um grupo de endpoints relacionados.
# Os routers são registrados no app/main.py.
#
# Regras:
#   1. Routers são THIN (magros) — só validam e delegam.
#   2. A validação de entrada é feita pelos schemas Pydantic.
#   3. A lógica de negócio é delegada aos services.
#   4. A autenticação é feita via Depends(obter_usuario_atual).
# ============================================================
