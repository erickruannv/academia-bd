import tkinter as tk
from tkinter import messagebox, ttk
import re
from decimal import Decimal
import psycopg2
import psycopg2.errors
from conexao import conectar, definir_janela_principal, ConexaoCancelada
from seguranca import gerar_hash, verificar_senha
import banco_alunos
from banco_alunos import AlunoDuplicado
import banco_matriculas
from banco_matriculas import MatriculaInvalida
import banco_pagamentos
import banco_relatorios

TAMANHO_MAX_LOGIN = 50  # usuarios.login e VARCHAR(50)

def autenticar(usuario, senha):
    # Busca a senha salva e compara no Python: aceita hash PBKDF2 e contas antigas em texto puro
    conn = conectar()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT senha FROM usuarios WHERE login = %s", (usuario,))
            resultado = cur.fetchone()
        finally:
            cur.close()
    finally:
        conn.close()
    return resultado is not None and verificar_senha(senha, resultado[0])

def cadastrar_usuario(usuario, senha):
    # Retorna False se o usuario ja existir
    senha_hash = gerar_hash(senha)
    conn = conectar()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 FROM usuarios WHERE login = %s", (usuario,))
            if cur.fetchone() is not None:
                conn.rollback()
                return False
            cur.execute("INSERT INTO usuarios (login, senha) VALUES (%s, %s)", (usuario, senha_hash))
            conn.commit()
            return True
        except psycopg2.errors.UniqueViolation:
            # Outro cadastro com o mesmo login entrou entre a verificacao e o INSERT
            conn.rollback()
            return False
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        conn.close()

class TelaLogin:
    def __init__(self, janela, usuario=""):
        self.janela = janela
        janela.title("Academia FitLife")
        janela.resizable(False, False)

        quadro = tk.Frame(janela, padx=20, pady=20)
        quadro.pack()
        self.quadro = quadro

        tk.Label(quadro, text="Academia FitLife", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(quadro, text="Usuario:").grid(row=1, column=0, sticky="e", pady=5)
        self.entrada_usuario = tk.Entry(quadro, width=25)
        self.entrada_usuario.insert(0, usuario)
        self.entrada_usuario.grid(row=1, column=1, pady=5)

        tk.Label(quadro, text="Senha:").grid(row=2, column=0, sticky="e", pady=5)
        self.entrada_senha = tk.Entry(quadro, width=25, show="*")
        self.entrada_senha.grid(row=2, column=1, pady=5)

        tk.Button(quadro, text="Entrar", width=15, command=self.entrar).grid(
            row=3, column=0, columnspan=2, pady=(15, 0))
        tk.Button(quadro, text="Criar conta", width=15, command=self.criar_conta).grid(
            row=4, column=0, columnspan=2, pady=(5, 0))

        # Enter tambem aciona o botao Entrar
        janela.bind("<Return>", lambda _evento: self.entrar())
        if usuario:
            self.entrada_senha.focus_set()
        else:
            self.entrada_usuario.focus_set()

    def criar_conta(self):
        self.janela.unbind("<Return>")
        self.quadro.destroy()
        TelaCadastro(self.janela)

    def entrar(self):
        usuario = self.entrada_usuario.get().strip()
        senha = self.entrada_senha.get()
        if not usuario or not senha:
            messagebox.showwarning("Login", "Preencha usuario e senha.", parent=self.janela)
            return
        try:
            ok = autenticar(usuario, senha)
        except ConexaoCancelada:
            # Usuario cancelou a senha do PostgreSQL: continua na tela de login
            return
        except psycopg2.Error as e:
            messagebox.showerror("Falha na conexao", str(e), parent=self.janela)
            return

        if ok:
            messagebox.showinfo("Login", f"Bem-vindo, {usuario}!", parent=self.janela)
            # Troca o conteudo da mesma janela pela tela principal com abas
            self.janela.unbind("<Return>")
            self.quadro.destroy()
            TelaPrincipal(self.janela)
        else:
            messagebox.showerror("Login", "Usuario ou senha incorretos.", parent=self.janela)
            self.entrada_senha.delete(0, tk.END)
            self.entrada_senha.focus_set()

class TelaCadastro:
    def __init__(self, janela):
        self.janela = janela
        janela.title("Academia FitLife - Criar conta")
        janela.resizable(False, False)

        quadro = tk.Frame(janela, padx=20, pady=20)
        quadro.pack()
        self.quadro = quadro

        tk.Label(quadro, text="Criar conta", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(quadro, text="Usuario:").grid(row=1, column=0, sticky="e", pady=5)
        self.entrada_usuario = tk.Entry(quadro, width=25)
        self.entrada_usuario.grid(row=1, column=1, pady=5)

        tk.Label(quadro, text="Senha:").grid(row=2, column=0, sticky="e", pady=5)
        self.entrada_senha = tk.Entry(quadro, width=25, show="*")
        self.entrada_senha.grid(row=2, column=1, pady=5)

        tk.Label(quadro, text="Confirmar senha:").grid(row=3, column=0, sticky="e", pady=5)
        self.entrada_confirmacao = tk.Entry(quadro, width=25, show="*")
        self.entrada_confirmacao.grid(row=3, column=1, pady=5)

        tk.Button(quadro, text="Cadastrar", width=15, command=self.cadastrar).grid(
            row=4, column=0, columnspan=2, pady=(15, 0))
        tk.Button(quadro, text="Voltar", width=15, command=self.voltar).grid(
            row=5, column=0, columnspan=2, pady=(5, 0))

        janela.bind("<Return>", lambda _evento: self.cadastrar())
        self.entrada_usuario.focus_set()

    def voltar(self, usuario=""):
        self.janela.unbind("<Return>")
        self.quadro.destroy()
        TelaLogin(self.janela, usuario)

    def cadastrar(self):
        usuario = self.entrada_usuario.get().strip()
        senha = self.entrada_senha.get()
        confirmacao = self.entrada_confirmacao.get()
        if not usuario or not senha or not confirmacao:
            messagebox.showwarning("Criar conta", "Preencha usuario, senha e confirmacao.", parent=self.janela)
            return
        if len(usuario) > TAMANHO_MAX_LOGIN:
            messagebox.showwarning("Criar conta", f"O usuario deve ter no maximo {TAMANHO_MAX_LOGIN} caracteres.",
                                   parent=self.janela)
            return
        if senha != confirmacao:
            messagebox.showwarning("Criar conta", "As senhas nao conferem.", parent=self.janela)
            self.entrada_confirmacao.delete(0, tk.END)
            self.entrada_confirmacao.focus_set()
            return
        try:
            criado = cadastrar_usuario(usuario, senha)
        except ConexaoCancelada:
            # Senha do PostgreSQL cancelada: continua no formulario
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao criar conta", str(e), parent=self.janela)
            return
        if not criado:
            messagebox.showerror("Criar conta", f"O usuario \"{usuario}\" ja existe.", parent=self.janela)
            self.entrada_usuario.focus_set()
            return
        messagebox.showinfo("Criar conta", "Conta criada com sucesso. Faca o login.", parent=self.janela)
        self.voltar(usuario)

def formatar_reais(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data):
    return data.strftime("%d/%m/%Y") if data else ""

class TelaMatriculas:
    def __init__(self, janela, pai, ao_alterar):
        self.janela = janela
        # Chamado depois de criar, alterar ou excluir, para atualizar as outras abas
        self.ao_alterar = ao_alterar

        quadro = tk.Frame(pai, padx=15, pady=15)
        quadro.pack(fill="both", expand=True)

        tk.Label(quadro, text="Matriculas", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        area = tk.Frame(quadro)
        area.pack(fill="both", expand=True)

        self.tabela = ttk.Treeview(area, columns=("aluno", "plano", "status", "inicio", "fim"), show="headings",
                                   height=12, selectmode="browse")
        self.tabela.heading("aluno", text="Aluno")
        self.tabela.heading("plano", text="Plano")
        self.tabela.heading("status", text="Situacao")
        self.tabela.heading("inicio", text="Inicio")
        self.tabela.heading("fim", text="Vencimento")
        self.tabela.column("aluno", width=250)
        self.tabela.column("plano", width=150)
        self.tabela.column("status", width=110, anchor="center")
        self.tabela.column("inicio", width=100, anchor="center")
        self.tabela.column("fim", width=100, anchor="center")

        rolagem = ttk.Scrollbar(area, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")

        botoes = tk.Frame(quadro)
        botoes.pack(pady=(10, 0))
        tk.Button(botoes, text="Nova matricula", width=15, command=self.nova).pack(side="left", padx=5)
        tk.Button(botoes, text="Alterar situacao", width=15, command=self.alterar_situacao).pack(side="left", padx=5)
        tk.Button(botoes, text="Excluir", width=15, command=self.excluir).pack(side="left", padx=5)
        tk.Button(botoes, text="Atualizar", width=15, command=self.atualizar).pack(side="left", padx=5)

        # Dados completos de cada linha, pela chave id_matricula (iid da tabela)
        self.matriculas = {}
        self.atualizar()

    def atualizar(self):
        try:
            linhas = banco_matriculas.listar_matriculas()
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao consultar matriculas", str(e), parent=self.janela)
            return
        self.tabela.delete(*self.tabela.get_children())
        self.matriculas = {}
        for id_matricula, aluno, plano, status, inicio, fim in linhas:
            self.matriculas[str(id_matricula)] = (id_matricula, aluno, plano, status)
            self.tabela.insert("", tk.END, iid=str(id_matricula),
                               values=(aluno, plano, status, formatar_data(inicio), formatar_data(fim)))

    def _selecionada(self, acao):
        selecao = self.tabela.selection()
        if not selecao:
            messagebox.showwarning("Matriculas", f"Selecione uma matricula na tabela para {acao}.",
                                   parent=self.janela)
            return None
        return self.matriculas[selecao[0]]

    def _depois_de_alterar(self):
        self.atualizar()
        self.ao_alterar()

    def nova(self):
        try:
            alunos = banco_matriculas.listar_alunos()
            planos = banco_matriculas.listar_planos()
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao carregar alunos e planos", str(e), parent=self.janela)
            return
        if not alunos or not planos:
            messagebox.showwarning("Nova matricula", "Cadastre ao menos um aluno e um plano antes.",
                                   parent=self.janela)
            return
        FormularioMatricula(self.janela, alunos, planos, self._depois_de_alterar)

    def alterar_situacao(self):
        matricula = self._selecionada("alterar a situacao")
        if matricula is not None:
            FormularioSituacao(self.janela, matricula, self._depois_de_alterar)

    def excluir(self):
        matricula = self._selecionada("excluir")
        if matricula is None:
            return
        id_matricula, aluno, plano, status = matricula
        try:
            pagamentos = banco_matriculas.contar_pagamentos(id_matricula)
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao excluir matricula", str(e), parent=self.janela)
            return
        confirmar = messagebox.askyesno(
            "Excluir matricula",
            f"Excluir a matricula {id_matricula} de \"{aluno}\" no plano {plano} ({status})?\n\n"
            f"Tambem serao apagados {pagamentos} pagamento(s) desta matricula.\n\n"
            "Essa acao nao pode ser desfeita.",
            icon="warning", default="no", parent=self.janela)
        if not confirmar:
            return
        try:
            excluida = banco_matriculas.excluir_matricula(id_matricula)
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao excluir matricula", str(e), parent=self.janela)
            return
        self._depois_de_alterar()
        if excluida:
            messagebox.showinfo("Excluir matricula", f"Matricula {id_matricula} excluida.", parent=self.janela)
        else:
            messagebox.showwarning("Excluir matricula", "Esta matricula ja havia sido excluida.",
                                   parent=self.janela)

class TelaPagamentos:
    def __init__(self, janela, pai):
        self.janela = janela

        quadro = tk.Frame(pai, padx=15, pady=15)
        quadro.pack(fill="both", expand=True)

        tk.Label(quadro, text="Pagamentos", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        pagamento = tk.LabelFrame(quadro, text="Registrar pagamento", padx=10, pady=10)
        pagamento.pack(fill="x", pady=(0, 15))

        tk.Label(pagamento, text="Matricula ativa:").grid(row=0, column=0, sticky="e")
        self.combo_matricula = ttk.Combobox(pagamento, state="readonly", width=60)
        self.combo_matricula.grid(row=0, column=1, columnspan=5, padx=5, pady=(0, 5), sticky="w")
        tk.Label(pagamento, text="Valor (R$):").grid(row=1, column=0, sticky="e")
        self.entrada_valor = tk.Entry(pagamento, width=12)
        self.entrada_valor.grid(row=1, column=1, padx=5, sticky="w")
        tk.Label(pagamento, text="Forma:").grid(row=1, column=2, sticky="e")
        self.combo_forma = ttk.Combobox(pagamento, values=banco_pagamentos.FORMAS, state="readonly", width=10)
        self.combo_forma.current(0)
        self.combo_forma.grid(row=1, column=3, padx=5)
        tk.Button(pagamento, text="Registrar", width=12, command=self.registrar).grid(row=1, column=4, padx=5)

        area = tk.Frame(quadro)
        area.pack(fill="both", expand=True)

        self.tabela = ttk.Treeview(area, columns=("aluno", "plano", "valor", "forma", "data"), show="headings",
                                   height=12, selectmode="browse")
        self.tabela.heading("aluno", text="Aluno")
        self.tabela.heading("plano", text="Plano")
        self.tabela.heading("valor", text="Valor")
        self.tabela.heading("forma", text="Forma")
        self.tabela.heading("data", text="Data")
        self.tabela.column("aluno", width=250)
        self.tabela.column("plano", width=130)
        self.tabela.column("valor", width=110, anchor="e")
        self.tabela.column("forma", width=100, anchor="center")
        self.tabela.column("data", width=100, anchor="center")

        rolagem = ttk.Scrollbar(area, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")

        botoes = tk.Frame(quadro)
        botoes.pack(pady=(10, 0))
        tk.Button(botoes, text="Atualizar", width=18, command=self.atualizar).pack(side="left", padx=5)
        tk.Button(botoes, text="Excluir selecionado", width=18, command=self.excluir).pack(side="left", padx=5)

        # Dados completos pela chave id (iid da tabela) e matriculas na ordem do combo
        self.pagamentos = {}
        self.ativas = []
        self.atualizar()

    def atualizar(self):
        # Recarrega o historico e as matriculas ATIVAS do combo
        try:
            pagamentos = banco_pagamentos.listar_pagamentos()
            ativas = banco_pagamentos.listar_matriculas_ativas()
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao consultar pagamentos", str(e), parent=self.janela)
            return
        self.tabela.delete(*self.tabela.get_children())
        self.pagamentos = {}
        for id_pagamento, aluno, plano, valor, forma, data in pagamentos:
            self.pagamentos[str(id_pagamento)] = (id_pagamento, aluno, plano, valor, forma, data)
            self.tabela.insert("", tk.END, iid=str(id_pagamento),
                               values=(aluno, plano, formatar_reais(valor), forma or "", formatar_data(data)))

        # Mantem a matricula escolhida no combo se ela continua ATIVA
        anterior = self.combo_matricula.current()
        id_anterior = self.ativas[anterior][0] if anterior >= 0 else None
        self.ativas = ativas
        self.combo_matricula["values"] = [f"{nome} (CPF {cpf}) - {plano}" for _id, nome, cpf, plano in ativas]
        ids = [linha[0] for linha in ativas]
        if id_anterior in ids:
            self.combo_matricula.current(ids.index(id_anterior))
        else:
            self.combo_matricula.set("")

    def registrar(self):
        indice = self.combo_matricula.current()
        if indice < 0:
            messagebox.showwarning("Registrar pagamento", "Selecione uma matricula ativa.", parent=self.janela)
            return
        # Aceita virgula ou ponto e no maximo duas casas decimais
        texto_valor = self.entrada_valor.get().strip()
        if not re.fullmatch(r"\d+([.,]\d{1,2})?", texto_valor):
            messagebox.showwarning("Registrar pagamento",
                                   "Informe um valor valido, com ate duas casas decimais (ex.: 89,90).",
                                   parent=self.janela)
            return
        valor = Decimal(texto_valor.replace(",", "."))
        if valor <= 0:
            messagebox.showwarning("Registrar pagamento", "O valor deve ser maior que zero.", parent=self.janela)
            return
        id_matricula, aluno, _cpf, plano = self.ativas[indice]
        forma = self.combo_forma.get()
        try:
            banco_pagamentos.registrar_pagamento(id_matricula, valor, forma)
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            # Erros da Procedure (RAISE EXCEPTION) aparecem so com a mensagem principal
            mensagem = getattr(e.diag, "message_primary", None) or str(e)
            messagebox.showerror("Erro ao registrar pagamento", mensagem, parent=self.janela)
            self.atualizar()
            return
        self.entrada_valor.delete(0, tk.END)
        self.atualizar()
        messagebox.showinfo("Registrar pagamento",
                            f"Pagamento de {formatar_reais(valor)} ({forma}) registrado para \"{aluno}\" - {plano}.",
                            parent=self.janela)

    def excluir(self):
        selecao = self.tabela.selection()
        if not selecao:
            messagebox.showwarning("Pagamentos", "Selecione um pagamento na tabela para excluir.", parent=self.janela)
            return
        id_pagamento, aluno, plano, valor, forma, data = self.pagamentos[selecao[0]]
        confirmar = messagebox.askyesno(
            "Excluir pagamento",
            f"Excluir o pagamento de {formatar_reais(valor)} do aluno \"{aluno}\"?\n\n"
            f"Plano: {plano}\nForma: {forma or '-'}\nData: {formatar_data(data)}\n\n"
            "Essa acao nao pode ser desfeita.",
            icon="warning", default="no", parent=self.janela)
        if not confirmar:
            return
        try:
            excluido = banco_pagamentos.excluir_pagamento(id_pagamento)
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao excluir pagamento", str(e), parent=self.janela)
            return
        self.atualizar()
        if excluido:
            messagebox.showinfo("Excluir pagamento", "Pagamento excluido.", parent=self.janela)
        else:
            messagebox.showwarning("Excluir pagamento", "Este pagamento ja havia sido excluido.", parent=self.janela)

def _abrir_dialogo(janela, titulo):
    dialogo = tk.Toplevel(janela)
    dialogo.title(titulo)
    dialogo.resizable(False, False)
    dialogo.transient(janela)
    return dialogo

class FormularioMatricula:
    # Os IDs ficam nas listas; o usuario escolhe pelo nome do aluno e do plano
    def __init__(self, janela, alunos, planos, ao_salvar):
        self.janela = janela
        self.alunos = alunos
        self.planos = planos
        self.ao_salvar = ao_salvar

        self.dialogo = _abrir_dialogo(janela, "Nova matricula")
        quadro = tk.Frame(self.dialogo, padx=20, pady=20)
        quadro.pack()

        tk.Label(quadro, text="Aluno:").grid(row=0, column=0, sticky="e", pady=5)
        self.combo_aluno = ttk.Combobox(quadro, state="readonly", width=45,
                                        values=[f"{nome} (CPF {cpf})" for _id, nome, cpf in alunos])
        self.combo_aluno.grid(row=0, column=1, pady=5, padx=(5, 0))

        tk.Label(quadro, text="Plano:").grid(row=1, column=0, sticky="e", pady=5)
        self.combo_plano = ttk.Combobox(quadro, state="readonly", width=45, values=[
            f"{nome} - {formatar_reais(valor)} - {meses} mes(es)" for _id, nome, valor, meses in planos])
        self.combo_plano.grid(row=1, column=1, pady=5, padx=(5, 0))

        tk.Label(quadro, text="Inicio hoje; o vencimento e calculado pela duracao do plano.",
                 fg="gray30").grid(row=2, column=0, columnspan=2, pady=(5, 0))

        botoes = tk.Frame(quadro)
        botoes.grid(row=3, column=0, columnspan=2, pady=(15, 0))
        tk.Button(botoes, text="Salvar", width=12, command=self.salvar).pack(side="left", padx=5)
        tk.Button(botoes, text="Cancelar", width=12, command=self.dialogo.destroy).pack(side="left", padx=5)

        self.dialogo.bind("<Escape>", lambda _evento: self.dialogo.destroy())
        self.combo_aluno.focus_set()
        self.dialogo.grab_set()

    def salvar(self):
        indice_aluno = self.combo_aluno.current()
        indice_plano = self.combo_plano.current()
        if indice_aluno < 0 or indice_plano < 0:
            messagebox.showwarning("Nova matricula", "Selecione o aluno e o plano.", parent=self.dialogo)
            return
        id_aluno, nome_aluno = self.alunos[indice_aluno][:2]
        id_plano, nome_plano = self.planos[indice_plano][:2]
        try:
            banco_matriculas.cadastrar_matricula(id_aluno, id_plano)
        except ConexaoCancelada:
            return
        except MatriculaInvalida as e:
            messagebox.showerror("Nova matricula", str(e), parent=self.dialogo)
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao criar matricula", str(e), parent=self.dialogo)
            return
        self.dialogo.destroy()
        self.ao_salvar()
        messagebox.showinfo("Nova matricula", f"Matricula de \"{nome_aluno}\" no plano {nome_plano} criada.",
                            parent=self.janela)

class FormularioSituacao:
    def __init__(self, janela, matricula, ao_salvar):
        self.janela = janela
        self.id_matricula, aluno, plano, status = matricula
        self.ao_salvar = ao_salvar

        self.dialogo = _abrir_dialogo(janela, "Alterar situacao")
        quadro = tk.Frame(self.dialogo, padx=20, pady=20)
        quadro.pack()

        tk.Label(quadro, text=f"{aluno} - {plano}", font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(quadro, text=f"Situacao atual: {status}").pack(anchor="w", pady=(0, 10))

        self.situacao = tk.StringVar(value=status)
        for opcao in banco_matriculas.SITUACOES:
            tk.Radiobutton(quadro, text=opcao, value=opcao, variable=self.situacao).pack(anchor="w")

        botoes = tk.Frame(quadro)
        botoes.pack(pady=(15, 0))
        tk.Button(botoes, text="Salvar", width=12, command=self.salvar).pack(side="left", padx=5)
        tk.Button(botoes, text="Cancelar", width=12, command=self.dialogo.destroy).pack(side="left", padx=5)

        self.dialogo.bind("<Return>", lambda _evento: self.salvar())
        self.dialogo.bind("<Escape>", lambda _evento: self.dialogo.destroy())
        self.dialogo.grab_set()

    def salvar(self):
        status = self.situacao.get()
        try:
            banco_matriculas.alterar_situacao(self.id_matricula, status)
        except ConexaoCancelada:
            return
        except MatriculaInvalida as e:
            messagebox.showerror("Alterar situacao", str(e), parent=self.dialogo)
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao alterar situacao", str(e), parent=self.dialogo)
            return
        self.dialogo.destroy()
        self.ao_salvar()
        messagebox.showinfo("Alterar situacao", f"Situacao da matricula {self.id_matricula} alterada para {status}.",
                            parent=self.janela)

class FormularioAluno:
    # Janela de cadastro/edicao; dados=None cadastra, senao edita o aluno informado
    def __init__(self, janela, ao_salvar, dados=None):
        self.janela = janela
        self.ao_salvar = ao_salvar
        self.id_aluno = dados[0] if dados else None

        self.dialogo = tk.Toplevel(janela)
        self.dialogo.title("Editar aluno" if dados else "Cadastrar aluno")
        self.dialogo.resizable(False, False)
        self.dialogo.transient(janela)

        quadro = tk.Frame(self.dialogo, padx=20, pady=20)
        quadro.pack()

        self.entradas = []
        rotulos = ("Nome:", "CPF (11 numeros):", "Telefone:", "E-mail:")
        for linha, rotulo in enumerate(rotulos):
            tk.Label(quadro, text=rotulo).grid(row=linha, column=0, sticky="e", pady=5)
            entrada = tk.Entry(quadro, width=35)
            entrada.grid(row=linha, column=1, pady=5, padx=(5, 0))
            if dados:
                entrada.insert(0, dados[linha + 1] or "")
            self.entradas.append(entrada)

        botoes = tk.Frame(quadro)
        botoes.grid(row=len(rotulos), column=0, columnspan=2, pady=(15, 0))
        tk.Button(botoes, text="Salvar", width=12, command=self.salvar).pack(side="left", padx=5)
        tk.Button(botoes, text="Cancelar", width=12, command=self.dialogo.destroy).pack(side="left", padx=5)

        self.dialogo.bind("<Return>", lambda _evento: self.salvar())
        self.dialogo.bind("<Escape>", lambda _evento: self.dialogo.destroy())
        self.entradas[0].focus_set()
        # Modal: bloqueia a janela principal enquanto o formulario estiver aberto
        self.dialogo.grab_set()

    def salvar(self):
        try:
            dados = banco_alunos.preparar_dados(*(entrada.get() for entrada in self.entradas))
        except ValueError as e:
            messagebox.showwarning("Aluno", str(e), parent=self.dialogo)
            return
        try:
            if self.id_aluno is None:
                banco_alunos.cadastrar_aluno(*dados)
                mensagem = "Aluno cadastrado com sucesso."
            elif banco_alunos.atualizar_aluno(self.id_aluno, *dados):
                mensagem = "Aluno atualizado com sucesso."
            else:
                messagebox.showerror("Aluno", "Este aluno nao existe mais. A lista sera atualizada.",
                                     parent=self.dialogo)
                self.dialogo.destroy()
                self.ao_salvar()
                return
        except ConexaoCancelada:
            return
        except AlunoDuplicado as e:
            messagebox.showerror("Aluno", str(e), parent=self.dialogo)
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao salvar aluno", str(e), parent=self.dialogo)
            return
        self.dialogo.destroy()
        self.ao_salvar()
        messagebox.showinfo("Aluno", mensagem, parent=self.janela)

class TelaAlunos:
    def __init__(self, janela, pai, ao_alterar):
        self.janela = janela
        # Chamado depois de salvar ou excluir, para atualizar as outras abas
        self.ao_alterar = ao_alterar

        quadro = tk.Frame(pai, padx=15, pady=15)
        quadro.pack(fill="both", expand=True)

        tk.Label(quadro, text="Alunos", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        busca = tk.Frame(quadro)
        busca.pack(fill="x", pady=(0, 10))
        tk.Label(busca, text="Buscar por nome ou CPF:").pack(side="left")
        self.entrada_busca = tk.Entry(busca, width=30)
        self.entrada_busca.pack(side="left", padx=5)
        self.entrada_busca.bind("<Return>", lambda _evento: self.atualizar())
        tk.Button(busca, text="Buscar", width=10, command=self.atualizar).pack(side="left", padx=5)
        tk.Button(busca, text="Limpar", width=10, command=self.limpar_busca).pack(side="left")

        area = tk.Frame(quadro)
        area.pack(fill="both", expand=True)

        self.tabela = ttk.Treeview(area, columns=("nome", "cpf", "telefone", "email"), show="headings",
                                   height=12, selectmode="browse")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("cpf", text="CPF")
        self.tabela.heading("telefone", text="Telefone")
        self.tabela.heading("email", text="E-mail")
        self.tabela.column("nome", width=220)
        self.tabela.column("cpf", width=110, anchor="center")
        self.tabela.column("telefone", width=130)
        self.tabela.column("email", width=220)
        # Duplo clique abre a edicao da linha
        self.tabela.bind("<Double-1>", lambda _evento: self.editar())

        rolagem = ttk.Scrollbar(area, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")

        botoes = tk.Frame(quadro)
        botoes.pack(pady=(10, 0))
        tk.Button(botoes, text="Cadastrar", width=12, command=self.cadastrar).pack(side="left", padx=5)
        tk.Button(botoes, text="Editar", width=12, command=self.editar).pack(side="left", padx=5)
        tk.Button(botoes, text="Excluir", width=12, command=self.excluir).pack(side="left", padx=5)
        tk.Button(botoes, text="Atualizar", width=12, command=self.atualizar).pack(side="left", padx=5)

        self.total = tk.Label(quadro, text="")
        self.total.pack(pady=(5, 0))

        # Dados completos de cada linha, pela chave id_aluno (iid da tabela)
        self.alunos = {}
        self.atualizar()

    def atualizar(self):
        try:
            linhas = banco_alunos.listar_alunos(self.entrada_busca.get())
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao consultar alunos", str(e), parent=self.janela)
            return
        self.tabela.delete(*self.tabela.get_children())
        self.alunos = {}
        for linha in linhas:
            self.alunos[str(linha[0])] = linha
            # Telefone e e-mail NULL aparecem vazios
            self.tabela.insert("", tk.END, iid=str(linha[0]), values=[v or "" for v in linha[1:]])
        self.total.config(text=f"{len(linhas)} aluno(s) encontrado(s)")

    def limpar_busca(self):
        self.entrada_busca.delete(0, tk.END)
        self.atualizar()

    def _depois_de_alterar(self):
        self.atualizar()
        self.ao_alterar()

    def _selecionado(self, acao):
        selecao = self.tabela.selection()
        if not selecao:
            messagebox.showwarning("Alunos", f"Selecione um aluno na tabela para {acao}.", parent=self.janela)
            return None
        return self.alunos[selecao[0]]

    def cadastrar(self):
        FormularioAluno(self.janela, self._depois_de_alterar)

    def editar(self):
        aluno = self._selecionado("editar")
        if aluno is not None:
            FormularioAluno(self.janela, self._depois_de_alterar, aluno)

    def excluir(self):
        aluno = self._selecionado("excluir")
        if aluno is None:
            return
        id_aluno, nome, cpf = aluno[0], aluno[1], aluno[2]
        try:
            matriculas, pagamentos = banco_alunos.contar_vinculos(id_aluno)
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao excluir aluno", str(e), parent=self.janela)
            return
        confirmar = messagebox.askyesno(
            "Excluir aluno",
            f"Excluir o aluno \"{nome}\" (CPF {cpf})?\n\n"
            f"Tambem serao apagados {matriculas} matricula(s) e {pagamentos} pagamento(s) "
            "relacionados a este aluno.\n\nEssa acao nao pode ser desfeita.",
            icon="warning", default="no", parent=self.janela)
        if not confirmar:
            return
        try:
            excluido = banco_alunos.excluir_aluno(id_aluno)
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao excluir aluno", str(e), parent=self.janela)
            return
        self._depois_de_alterar()
        if excluido:
            messagebox.showinfo("Excluir aluno", f"Aluno \"{nome}\" excluido.", parent=self.janela)
        else:
            messagebox.showwarning("Excluir aluno", "Este aluno ja havia sido excluido.", parent=self.janela)

class TabelaRelatorio:
    # Tabela de um relatorio; embaixo mostra a quantidade de registros ou o aviso de vazio
    def __init__(self, pai, colunas):
        quadro = tk.Frame(pai, padx=10, pady=10)
        quadro.pack(fill="both", expand=True)

        area = tk.Frame(quadro)
        area.pack(fill="both", expand=True)
        self.tabela = ttk.Treeview(area, columns=[coluna[0] for coluna in colunas], show="headings", height=10)
        for chave, titulo, largura, alinhamento in colunas:
            self.tabela.heading(chave, text=titulo)
            self.tabela.column(chave, width=largura, anchor=alinhamento)
        rolagem = ttk.Scrollbar(area, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")

        self.situacao = tk.Label(quadro, text="")
        self.situacao.pack(pady=(5, 0))

    def mostrar(self, linhas):
        self.tabela.delete(*self.tabela.get_children())
        for linha in linhas:
            self.tabela.insert("", tk.END, values=linha)
        if linhas:
            self.situacao.config(text=f"{len(linhas)} registro(s)")
        else:
            self.situacao.config(text="Nenhum registro encontrado.")

class TelaRelatorios:
    def __init__(self, janela, pai):
        self.janela = janela

        quadro = tk.Frame(pai, padx=15, pady=15)
        quadro.pack(fill="both", expand=True)

        tk.Label(quadro, text="Relatorios", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        total = tk.LabelFrame(quadro, text="Total pago por aluno", padx=10, pady=10)
        total.pack(fill="x")
        tk.Label(total, text="Aluno:").grid(row=0, column=0, sticky="e")
        self.combo_aluno = ttk.Combobox(total, state="readonly", width=45)
        self.combo_aluno.grid(row=0, column=1, padx=5)
        tk.Button(total, text="Consultar", width=12, command=self.consultar_total).grid(row=0, column=2, padx=5)
        self.rotulo_total = tk.Label(total, text="", font=("Arial", 11, "bold"))
        self.rotulo_total.grid(row=0, column=3, padx=10, sticky="w")

        self.relatorios = ttk.Notebook(quadro)
        self.relatorios.pack(fill="both", expand=True, pady=(15, 0))
        self.ativas = TabelaRelatorio(self._aba("Matriculas ativas"), (
            ("aluno", "Aluno", 250, "w"), ("plano", "Plano", 130, "w"),
            ("inicio", "Inicio", 100, "center"), ("fim", "Vencimento", 100, "center")))
        self.todos = TabelaRelatorio(self._aba("Todos os alunos"), (
            ("aluno", "Aluno", 220, "w"), ("cpf", "CPF", 110, "center"), ("email", "E-mail", 200, "w"),
            ("plano", "Plano", 110, "w"), ("status", "Situacao", 100, "center")))
        self.vencendo = TabelaRelatorio(self._aba("Vencendo em 30 dias"), (
            ("aluno", "Aluno", 220, "w"), ("telefone", "Telefone", 130, "w"), ("plano", "Plano", 110, "w"),
            ("fim", "Vencimento", 100, "center"), ("dias", "Faltam", 90, "center")))

        tk.Button(quadro, text="Atualizar", width=15, command=self.atualizar).pack(pady=(10, 0))

        # Alunos na ordem do combo; o ID fica so aqui
        self.alunos = []
        self.atualizar()

    def _aba(self, titulo):
        aba = tk.Frame(self.relatorios)
        self.relatorios.add(aba, text=titulo)
        return aba

    def atualizar(self):
        try:
            alunos = banco_relatorios.listar_alunos()
            ativas = banco_relatorios.matriculas_ativas()
            todos = banco_relatorios.todos_alunos()
            vencendo = banco_relatorios.vencendo_30_dias()
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao consultar relatorios", str(e), parent=self.janela)
            return

        # Mantem o aluno escolhido no combo se ele ainda existe
        anterior = self.combo_aluno.current()
        id_anterior = self.alunos[anterior][0] if anterior >= 0 else None
        self.alunos = alunos
        self.combo_aluno["values"] = [f"{nome} (CPF {cpf})" for _id, nome, cpf in alunos]
        ids = [linha[0] for linha in alunos]
        self.rotulo_total.config(text="")
        if id_anterior in ids:
            self.combo_aluno.current(ids.index(id_anterior))
            # Recalcula: pagamentos podem ter mudado desde a ultima consulta
            self.consultar_total()
        else:
            self.combo_aluno.set("")

        self.ativas.mostrar([(aluno, plano, formatar_data(inicio), formatar_data(fim))
                             for aluno, plano, inicio, fim in ativas])
        self.todos.mostrar([(nome, cpf, email or "", plano, status) for nome, cpf, email, plano, status in todos])
        self.vencendo.mostrar([(nome, telefone or "", plano, formatar_data(fim), "hoje" if dias == 0 else f"{dias} dia(s)")
                               for nome, telefone, plano, fim, dias in vencendo])

    def consultar_total(self):
        indice = self.combo_aluno.current()
        if indice < 0:
            messagebox.showwarning("Total pago", "Selecione um aluno.", parent=self.janela)
            return
        id_aluno, nome, _cpf = self.alunos[indice]
        try:
            valor = banco_relatorios.total_pago_aluno(id_aluno)
        except ConexaoCancelada:
            return
        except psycopg2.Error as e:
            messagebox.showerror("Erro ao consultar total pago", str(e), parent=self.janela)
            return
        if valor is None:
            self.rotulo_total.config(text=f"{nome}: sem valor retornado")
        else:
            self.rotulo_total.config(text=f"{nome}: {formatar_reais(valor)}")

class TelaPrincipal:
    def __init__(self, janela):
        janela.title("Academia FitLife")
        janela.resizable(True, True)

        abas = ttk.Notebook(janela)
        abas.pack(fill="both", expand=True)
        aba_alunos = tk.Frame(abas)
        aba_matriculas = tk.Frame(abas)
        aba_pagamentos = tk.Frame(abas)
        aba_relatorios = tk.Frame(abas)
        abas.add(aba_alunos, text="Alunos")
        abas.add(aba_matriculas, text="Matriculas")
        abas.add(aba_pagamentos, text="Pagamentos")
        abas.add(aba_relatorios, text="Relatorios")

        self.relatorios = TelaRelatorios(janela, aba_relatorios)
        # Os relatorios dependem das outras tres abas: recarrega sempre que a aba e aberta
        abas.bind("<<NotebookTabChanged>>",
                  lambda _evento: abas.select() == str(aba_relatorios) and self.relatorios.atualizar())

        self.pagamentos = TelaPagamentos(janela, aba_pagamentos)
        # Matriculas novas, alteradas ou excluidas mudam o combo de ativas e o historico (cascata)
        self.matriculas = TelaMatriculas(janela, aba_matriculas, self.pagamentos.atualizar)
        # Alterar ou excluir aluno muda as listas de matriculas e pagamentos (nome e exclusao em cascata)
        self.alunos = TelaAlunos(janela, aba_alunos, self._aluno_alterado)

    def _aluno_alterado(self):
        self.matriculas.atualizar()
        self.pagamentos.atualizar()

def iniciar():
    janela = tk.Tk()
    definir_janela_principal(janela)
    TelaLogin(janela)
    janela.mainloop()

if __name__ == "__main__":
    iniciar()
