import flet as ft

from api import criar_usuario, fazer_login, listar_usuarios


def main(pagina: ft.Page):
    pagina.title = "FinTrack"
    pagina.theme_mode = ft.ThemeMode.LIGHT
    pagina.window.width = 700
    pagina.window.height = 500
    pagina.window.resizable = False
    pagina.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    pagina.vertical_alignment = ft.MainAxisAlignment.CENTER

    token = None

    def limpar_erro(e):
        texto_erro.visible = False
        pagina.update()

    def mostrar_login():
        dashboard_column.visible = False
        cadastro_column.visible = False
        login_column.visible = True
        texto_erro.visible = False
        pagina.update()

    def mostrar_dashboard():
        login_column.visible = False
        cadastro_column.visible = False
        carregar_usuarios()
        dashboard_column.visible = True
        pagina.update()

    def sair(e):
        nonlocal token
        token = None
        mostrar_login()

    def ir_para_cadastro(e):
        login_column.visible = False
        cadastro_column.visible = True
        texto_erro.visible = False
        pagina.update()

    def ir_para_login(e):
        cadastro_column.visible = False
        login_column.visible = True
        texto_erro.visible = False
        pagina.update()

    def logar(e):
        nonlocal token
        email = campo_email.value
        senha = campo_senha.value

        if not email or not senha:
            texto_erro.value = "Preencha todos os campos"
            texto_erro.visible = True
            pagina.update()
            return

        btn_entrar.disabled = True
        btn_entrar.text = "Entrando..."
        pagina.update()

        dados = fazer_login(email, senha)

        if dados:
            token = dados["acesso_token"]
            texto_erro.visible = False
            mostrar_dashboard()
        else:
            texto_erro.value = "Email ou senha incorretos"
            texto_erro.visible = True
            btn_entrar.disabled = False
            btn_entrar.text = "Entrar"
            pagina.update()

    def cadastrar(e):
        nome = campo_nome.value
        email = campo_email_cadastro.value
        senha = campo_senha_cadastro.value

        if not nome or not email or not senha:
            texto_erro.value = "Preencha todos os campos"
            texto_erro.visible = True
            pagina.update()
            return

        btn_cadastrar.disabled = True
        btn_cadastrar.text = "Cadastrando..."
        pagina.update()

        dados = criar_usuario(nome, email, senha)

        if dados:
            texto_erro.visible = False
            pagina.snack_bar = ft.SnackBar(
                ft.Text("Conta criada! Faça login."),
                bgcolor=ft.Colors.GREEN,
            )
            pagina.snack_bar.open = True
            ir_para_login(None)
        else:
            texto_erro.value = "Email já cadastrado ou dados inválidos"
            texto_erro.visible = True

        btn_cadastrar.disabled = False
        btn_cadastrar.text = "Cadastrar"
        pagina.update()

    def carregar_usuarios():
        if not token:
            return

        usuarios = listar_usuarios(token)
        tabela.rows.clear()

        for usuario in usuarios:
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(usuario["id"]))),
                        ft.DataCell(ft.Text(usuario["nome"])),
                        ft.DataCell(ft.Text(usuario["email"])),
                    ]
                )
            )
        pagina.update()

    # --- Tela de Login ---
    campo_email = ft.TextField(
        label="Email",
        hint_text="seu@email.com",
        prefix_icon=ft.Icons.EMAIL,
        width=300,
        on_change=limpar_erro,
    )
    campo_senha = ft.TextField(
        label="Senha",
        hint_text="Digite sua senha",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        width=300,
        on_change=limpar_erro,
    )
    btn_entrar = ft.Button("Entrar", width=300, on_click=logar)
    link_cadastro = ft.TextButton(
        "Não tem conta? Cadastre-se",
        on_click=ir_para_cadastro,
    )
    login_column = ft.Column(
        [
            ft.Text("FinTrack", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Controle Financeiro", size=14, color=ft.Colors.GREY),
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            campo_email,
            campo_senha,
            btn_entrar,
            link_cadastro,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # --- Tela de Cadastro ---
    campo_nome = ft.TextField(
        label="Nome completo",
        hint_text="Seu nome",
        prefix_icon=ft.Icons.PERSON,
        width=300,
        on_change=limpar_erro,
    )
    campo_email_cadastro = ft.TextField(
        label="Email",
        hint_text="seu@email.com",
        prefix_icon=ft.Icons.EMAIL,
        width=300,
        on_change=limpar_erro,
    )
    campo_senha_cadastro = ft.TextField(
        label="Senha",
        hint_text="Mínimo 6 caracteres",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        width=300,
        on_change=limpar_erro,
    )
    btn_cadastrar = ft.Button("Cadastrar", width=300, on_click=cadastrar)
    link_login = ft.TextButton(
        "Já tem conta? Faça login",
        on_click=ir_para_login,
    )
    cadastro_column = ft.Column(
        [
            ft.Text("Criar Conta", size=32, weight=ft.FontWeight.BOLD),
            ft.Text("Preencha os dados abaixo", size=14, color=ft.Colors.GREY),
            ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
            campo_nome,
            campo_email_cadastro,
            campo_senha_cadastro,
            btn_cadastrar,
            link_login,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False,
    )

    # --- Tela Dashboard (lista de usuários) ---
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Email")),
        ],
        rows=[],
        width=600,
    )

    dashboard_column = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Usuários Cadastrados", size=24, weight=ft.FontWeight.BOLD),
                    ft.IconButton(ft.Icons.LOGOUT, tooltip="Sair", on_click=sair),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(),
            ft.Container(content=tabela, padding=10),
        ],
        visible=False,
    )

    # --- Texto de Erro ---
    texto_erro = ft.Text("", color=ft.Colors.RED, size=13, visible=False)

    pagina.add(
        ft.Container(
            content=ft.Column(
                [texto_erro, login_column, cadastro_column, dashboard_column],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=30,
        )
    )


ft.app(target=main)
