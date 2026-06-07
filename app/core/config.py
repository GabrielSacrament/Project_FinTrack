# ============================================================
# app/core/config.py — Configurações da Aplicação
# ============================================================
# Técnica: Pydantic Settings (BaseSettings).
#
# BaseSettings é uma extensão do Pydantic que lê automaticamente
# variáveis de ambiente de um arquivo .env e as valida com
# base na tipagem Python.
#
# Vantagens:
#   - Validação automática de tipos (int, str, bool).
#   - Valores padrão definidos diretamente na classe.
#   - Acesso centralizado a todas as configurações.
#   - Compatível com o padrão 12 Factor App.
# ============================================================

from pydantic_settings import BaseSettings


# --- Classe de Configuração ---
class Configuracao(BaseSettings):
    """
    Configurações centralizadas da aplicação FinTrack.

    Herda de BaseSettings do Pydantic, que automaticamente:
    1. Lê variáveis do arquivo .env (definido via model_config).
    2. Converte os valores para os tipos Python declarados.
    3. Levanta erro se um valor obrigatório estiver faltando.

    Atributos:
        string_conexao_banco: URL de conexão com o SQLite.
        chave_secreta_jwt: Chave secreta para assinar tokens JWT.
        algoritmo_jwt: Algoritmo de criptografia do JWT (ex: HS256).
        expiracao_token_minutos: Tempo de expiração do token em minutos.
    """

    # --- Banco de Dados ---
    # Técnica: Field com default.
    # O valor será sobrescrito se a variável STRING_CONEXAO_BANCO
    # estiver definida no .env ou nas variáveis de ambiente.
    string_conexao_banco: str = "sqlite:///./fintrack.db"

    # --- JWT (JSON Web Token) ---
    chave_secreta_jwt: str = "super-secret-key"
    algoritmo_jwt: str = "HS256"
    expiracao_token_minutos: int = 30

    # --- Configuração do Pydantic Settings ---
    # Técnica: model_config com env_file.
    # Define que as variáveis devem ser lidas do arquivo .env.
    # O encoding utf-8 garante compatibilidade com caracteres especiais.
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# --- Instância Única (Singleton) ---
# Técnica: Instanciação no nível do módulo.
# Cria uma única instância de Config que é importada por
# todos os outros módulos. Isso evita ler o .env várias vezes.
config = Configuracao()
