import re
import psycopg2
import psycopg2.errors
from conexao import conectar

# Limites das colunas da tabela alunos
TAMANHO_MAX_NOME = 100
TAMANHO_CPF = 11
TAMANHO_MAX_TELEFONE = 20
TAMANHO_MAX_EMAIL = 100

# CPF ou e-mail ja usados por outro aluno (restricoes UNIQUE da tabela)
class AlunoDuplicado(Exception):
    pass

_DUPLICADOS = {
    "alunos_cpf_key": "Ja existe um aluno cadastrado com este CPF.",
    "alunos_email_key": "Ja existe um aluno cadastrado com este e-mail.",
}

def preparar_dados(nome, cpf, telefone, email):
    # Valida os campos do formulario; devolve os valores prontos para o banco
    # ou gera ValueError com a mensagem para o usuario
    nome = nome.strip()
    cpf = re.sub(r"[.\-\s]", "", cpf)  # aceita CPF digitado com pontos e traco
    telefone = telefone.strip() or None
    email = email.strip() or None
    if not nome:
        raise ValueError("Informe o nome do aluno.")
    if len(nome) > TAMANHO_MAX_NOME:
        raise ValueError(f"O nome deve ter no maximo {TAMANHO_MAX_NOME} caracteres.")
    if not re.fullmatch(r"\d{11}", cpf):
        raise ValueError(f"O CPF deve ter exatamente {TAMANHO_CPF} numeros.")
    if telefone is not None and len(telefone) > TAMANHO_MAX_TELEFONE:
        raise ValueError(f"O telefone deve ter no maximo {TAMANHO_MAX_TELEFONE} caracteres.")
    if email is not None:
        if len(email) > TAMANHO_MAX_EMAIL:
            raise ValueError(f"O e-mail deve ter no maximo {TAMANHO_MAX_EMAIL} caracteres.")
        if "@" not in email:
            raise ValueError("Informe um e-mail valido ou deixe o campo vazio.")
    return nome, cpf, telefone, email

def _escapar_like(texto):
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

def listar_alunos(termo=""):
    # Sem termo lista todos; com termo busca por parte do nome ou do CPF
    sql = "SELECT id_aluno, nome, cpf, telefone, email FROM alunos"
    parametros = ()
    termo = termo.strip()
    if termo:
        # Para o CPF ignora pontos e traco digitados na busca
        termo_cpf = re.sub(r"[.\-\s]", "", termo) or termo
        sql += " WHERE nome ILIKE %s OR cpf LIKE %s"
        parametros = ("%" + _escapar_like(termo) + "%", "%" + _escapar_like(termo_cpf) + "%")
    sql += " ORDER BY nome"
    conn = conectar()
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql, parametros)
            return cur.fetchall()
        finally:
            cur.close()
    finally:
        conn.close()

def _gravar(sql, parametros):
    # Executa INSERT/UPDATE/DELETE com commit; devolve quantas linhas foram afetadas
    conn = conectar()
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql, parametros)
            afetadas = cur.rowcount
            conn.commit()
            return afetadas
        except psycopg2.errors.UniqueViolation as e:
            conn.rollback()
            mensagem = _DUPLICADOS.get(e.diag.constraint_name, "CPF ou e-mail ja cadastrado para outro aluno.")
            raise AlunoDuplicado(mensagem) from None
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        conn.close()

def cadastrar_aluno(nome, cpf, telefone, email):
    _gravar("INSERT INTO alunos (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)",
            (nome, cpf, telefone, email))

def atualizar_aluno(id_aluno, nome, cpf, telefone, email):
    # Retorna False se o aluno nao existe mais (excluido em outra sessao)
    return _gravar("UPDATE alunos SET nome=%s, cpf=%s, telefone=%s, email=%s WHERE id_aluno=%s",
                   (nome, cpf, telefone, email, id_aluno)) > 0

def excluir_aluno(id_aluno):
    # Matriculas e pagamentos do aluno saem junto pelo ON DELETE CASCADE
    return _gravar("DELETE FROM alunos WHERE id_aluno = %s", (id_aluno,)) > 0

def contar_vinculos(id_aluno):
    # Quantidade de matriculas e pagamentos que serao apagados junto com o aluno
    conn = conectar()
    try:
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT (SELECT COUNT(*) FROM matriculas WHERE id_aluno = %s),
                       (SELECT COUNT(*)
                        FROM pagamentos pg
                        INNER JOIN matriculas m ON pg.id_matricula = m.id_matricula
                        WHERE m.id_aluno = %s)
            """, (id_aluno, id_aluno))
            return cur.fetchone()
        finally:
            cur.close()
    finally:
        conn.close()
