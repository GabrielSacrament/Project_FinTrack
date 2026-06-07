# ============================================================
# app/repositories/__init__.py
# ============================================================
# A pasta 'repositories' implementa o padrão Repository.
#
# Técnica: Repository Pattern.
# Cada repositório encapsula todas as operações de acesso a
# dados de uma entidade específica.
#
# Vantagens:
#   1. Isola a lógica de banco de dados do resto da aplicação.
#   2. Se mudarmos de ORM, só alteramos os repositórios.
#   3. Facilita testes (podemos mockar o repositório).
#   4. Evita repetição de queries (DRY).
# ============================================================
