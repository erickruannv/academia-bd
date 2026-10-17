import tkinter as tk
from tkinter import simpledialog, messagebox
import psycopg2

HOST = "127.0.0.1"
PORTA = 5433
BANCO = "academia"
USUARIO = "postgres"

# Senha guardada somente em memoria, pedida na primeira conexao e reutilizada
# por todo o programa; so e descartada se o PostgreSQL recusar a autenticacao
_senha = None

# Janela Tk principal da interface; se definida, os dialogos usam ela como pai
_janela_principal = None

# Usuario cancelou o pedido de senha; quem chamou volta para a tela em que estava
class ConexaoCancelada(Exception):
    pass

# Trechos das mensagens de falha de autenticacao (servidor em ingles ou portugues)
_FALHAS_AUTENTICACAO = (
    "password authentication failed",
    "no password supplied",
    "autenticação do tipo senha falhou",
    "nenhuma senha fornecida",
)

def definir_janela_principal(janela):
    global _janela_principal
    _janela_principal = janela

def _pedir_senha(mensagem):
    if _janela_principal is not None:
        return simpledialog.askstring("PostgreSQL", mensagem, show="*", parent=_janela_principal)
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    senha = simpledialog.askstring("PostgreSQL", mensagem, show="*", parent=root)
    root.destroy()
    return senha

def _abrir_conexao(senha):
    try:
        return psycopg2.connect(host=HOST, port=PORTA, database=BANCO, user=USUARIO,
                                password=senha, connect_timeout=5)
    except UnicodeDecodeError as e:
        # Servidor em portugues no Windows envia o erro em WIN1252 antes de
        # combinar a codificacao; o psycopg2 nao consegue ler e gera UnicodeDecodeError
        mensagem = e.object.decode("cp1252", errors="replace").strip()
        raise psycopg2.OperationalError(mensagem) from None

def _falha_de_autenticacao(erro):
    texto = str(erro).lower()
    return any(trecho in texto for trecho in _FALHAS_AUTENTICACAO)

def conectar():
    global _senha
    mensagem = "Senha do PostgreSQL:"
    while True:
        if _senha is None:
            senha = _pedir_senha(mensagem)
            if senha is None:
                raise ConexaoCancelada()
            _senha = senha
        try:
            return _abrir_conexao(_senha)
        except psycopg2.OperationalError as e:
            # Servidor fora do ar, timeout etc. nao invalidam a senha guardada
            if not _falha_de_autenticacao(e):
                raise
            _senha = None
            mensagem = "Senha do PostgreSQL incorreta. Tente novamente:"

def _mostrar(titulo, mensagem, erro=False):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    if erro:
        messagebox.showerror(titulo, mensagem, parent=root)
    else:
        messagebox.showinfo(titulo, mensagem, parent=root)
    root.destroy()

def testar_conexao():
    try:
        conn = conectar()
    except ConexaoCancelada:
        return
    except psycopg2.OperationalError as e:
        _mostrar("Falha na conexao", str(e), erro=True)
        return
    cur = conn.cursor()
    cur.execute("SELECT version()")
    versao = cur.fetchone()[0]
    cur.close()
    conn.close()
    _mostrar("Conexao OK", f"Conexao OK:\n{versao}\n\nConexao fechada.")

if __name__ == "__main__":
    testar_conexao()
