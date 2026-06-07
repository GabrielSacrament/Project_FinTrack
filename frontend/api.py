import requests

from config import URL_API


def fazer_login(email: str, senha: str) -> dict | None:
    resposta = requests.post(
        f"{URL_API}/usuarios/login",
        json={"email": email, "senha": senha},
    )
    if resposta.status_code == 200:
        return resposta.json()
    return None


def criar_usuario(nome: str, email: str, senha: str) -> dict | None:
    resposta = requests.post(
        f"{URL_API}/usuarios/",
        json={"nome": nome, "email": email, "senha": senha},
    )
    if resposta.status_code == 201:
        return resposta.json()
    return None


def listar_usuarios(token: str) -> list[dict]:
    resposta = requests.get(
        f"{URL_API}/usuarios/",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resposta.status_code == 200:
        return resposta.json()
    return []
