# ============================================================
# app/models/__init__.py
# ============================================================
# A pasta 'models' contém as entidades SQLAlchemy que mapeiam
# as tabelas do banco de dados relacional.
#
# Técnica: ORM (Object Relational Mapping).
# Cada classe herda de Base (definido em core/database.py) e
# representa uma tabela no banco. Cada atributo da classe
# representa uma coluna da tabela.
#
# Separação de responsabilidades:
#   - Models: apenas definição da estrutura das tabelas.
#   - Schemas: validação de dados de entrada/saída.
#   - Repositories: consultas/operações no banco.
#   - Services: regras de negócio.
# ============================================================
