# ============================================================
# app/services/__init__.py
# ============================================================
# A pasta 'services' contém as regras de negócio da aplicação.
#
# Técnica: Service Layer (Camada de Serviço).
# Os services orquestram repositórios e aplicam regras de
# negócio antes de persistir ou retornar dados.
#
# Regras:
#   1. Services NUNCA acessam o banco diretamente.
#   2. Services NUNCA recebem requisições HTTP.
#   3. Services usam repositórios para acesso a dados.
#   4. Services usam schemas para validação de entrada/saída.
#
# Isso garante SRP (Single Responsibility Principle) e
# testabilidade (podemos testar regras sem HTTP ou banco).
# ============================================================
