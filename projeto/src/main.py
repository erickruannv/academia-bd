import psycopg2

def conectar():
    return psycopg2.connect(host="localhost", database="academia", user="postgres", password="root")

def login():
    print("=== LOGIN ===")
    usuario = input("Usuario: ")
    senha = input("Senha: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE login = %s AND senha = %s", (usuario, senha))
    resultado = cur.fetchone()
    cur.close()
    conn.close()
    return resultado is not None

def cadastrar_aluno():
    print("\n--- Cadastrar Aluno ---")
    nome = input("Nome: ")
    cpf = input("CPF: ")
    telefone = input("Telefone: ")
    email = input("Email: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO alunos (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)",
                (nome, cpf, telefone, email))
    conn.commit()
    cur.close()
    conn.close()
    print("Aluno cadastrado!")

def listar_alunos():
    print("\n--- Lista de Alunos ---")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id_aluno, nome, cpf, telefone FROM alunos ORDER BY nome")
    alunos = cur.fetchall()
    cur.close()
    conn.close()
    for a in alunos:
        print(f"[{a[0]}] {a[1]} | CPF: {a[2]} | Tel: {a[3]}")

def buscar_aluno():
    print("\n--- Buscar Aluno ---")
    nome = input("Nome (ou parte): ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id_aluno, nome, cpf, telefone FROM alunos WHERE nome ILIKE %s ORDER BY nome",
                ("%" + nome + "%",))
    for a in cur.fetchall():
        print(f"[{a[0]}] {a[1]} | CPF: {a[2]} | Tel: {a[3]}")
    cur.close()
    conn.close()

def atualizar_aluno():
    listar_alunos()
    print("\n--- Atualizar Aluno ---")
    id_aluno = input("ID do aluno: ")
    nome = input("Novo nome: ")
    telefone = input("Novo telefone: ")
    email = input("Novo email: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE alunos SET nome=%s, telefone=%s, email=%s WHERE id_aluno=%s",
                (nome, telefone, email, id_aluno))
    conn.commit()
    cur.close()
    conn.close()
    print("Aluno atualizado!")

def excluir_aluno():
    listar_alunos()
    print("\n--- Excluir Aluno ---")
    id_aluno = input("ID do aluno: ")
    confirmar = input("Tem certeza? (s/n): ")
    if confirmar.lower() == "s":
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM alunos WHERE id_aluno = %s", (id_aluno,))
        conn.commit()
        cur.close()
        conn.close()
        print("Aluno excluido!")

def listar_planos():
    print("\n--- Planos Disponiveis ---")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id_plano, nome_plano, valor, duracao_meses FROM planos")
    for p in cur.fetchall():
        print(f"[{p[0]}] {p[1]} | R$ {p[2]} | {p[3]} mes(es)")
    cur.close()
    conn.close()

def cadastrar_matricula():
    listar_alunos()
    listar_planos()
    print("\n--- Cadastrar Matricula ---")
    id_aluno = input("ID do aluno: ")
    id_plano = input("ID do plano: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO matriculas (id_aluno, id_plano) VALUES (%s, %s)", (id_aluno, id_plano))
    conn.commit()
    cur.close()
    conn.close()
    print("Matricula criada!")

def atualizar_matricula():
    print("\n--- Atualizar Status da Matricula ---")
    id_matricula = input("ID da matricula: ")
    print("Status: 1-ATIVA  2-CANCELADA  3-VENCIDA")
    op = input("Escolha: ")
    status = {"1": "ATIVA", "2": "CANCELADA", "3": "VENCIDA"}.get(op)
    if status:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("UPDATE matriculas SET status=%s WHERE id_matricula=%s", (status, id_matricula))
        conn.commit()
        cur.close()
        conn.close()
        print("Status atualizado!")

def excluir_matricula():
    print("\n--- Excluir Matricula ---")
    id_matricula = input("ID da matricula: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM matriculas WHERE id_matricula = %s", (id_matricula,))
    conn.commit()
    cur.close()
    conn.close()
    print("Matricula excluida!")

def registrar_pagamento():
    print("\n--- Registrar Pagamento ---")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id_matricula, a.nome, p.nome_plano
        FROM matriculas m
        INNER JOIN alunos a ON m.id_aluno = a.id_aluno
        INNER JOIN planos p ON m.id_plano = p.id_plano
        WHERE m.status = 'ATIVA'
    """)
    for m in cur.fetchall():
        print(f"[{m[0]}] {m[1]} - {m[2]}")
    id_matricula = input("ID da matricula: ")
    valor = input("Valor pago: ")
    print("Forma: 1-PIX  2-CARTAO  3-DINHEIRO")
    op = input("Escolha: ")
    forma = {"1": "PIX", "2": "CARTAO", "3": "DINHEIRO"}.get(op)
    if forma:
        cur.execute("INSERT INTO pagamentos (id_matricula, valor_pago, forma_pagamento) VALUES (%s, %s, %s)",
                    (id_matricula, valor, forma))
        conn.commit()
        print("Pagamento registrado!")
    cur.close()
    conn.close()

def excluir_pagamento():
    print("\n--- Excluir Pagamento ---")
    id_pagamento = input("ID do pagamento: ")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM pagamentos WHERE id_pagamento = %s", (id_pagamento,))
    conn.commit()
    cur.close()
    conn.close()
    print("Pagamento excluido!")

def consulta_matriculas_ativas():
    print("\n--- Matriculas Ativas (INNER JOIN) ---")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.nome, p.nome_plano, m.data_inicio, m.data_fim, m.status
        FROM matriculas m
        INNER JOIN alunos a ON m.id_aluno = a.id_aluno
        INNER JOIN planos p ON m.id_plano = p.id_plano
        WHERE m.status = 'ATIVA'
        ORDER BY a.nome
    """)
    for r in cur.fetchall():
        print(f"{r[0]} | {r[1]} | inicio: {r[2]} | vence: {r[3]} | {r[4]}")
    cur.close()
    conn.close()

def consulta_todos_alunos():
    print("\n--- Todos os Alunos com Matricula (LEFT JOIN) ---")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.nome, a.email,
               COALESCE(p.nome_plano, 'Sem plano') AS plano,
               COALESCE(m.status, '-') AS status
        FROM alunos a
        LEFT JOIN matriculas m ON a.id_aluno = m.id_aluno
        LEFT JOIN planos p ON m.id_plano = p.id_plano
        ORDER BY a.nome
    """)
    for r in cur.fetchall():
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")
    cur.close()
    conn.close()

def consulta_pagamentos():
    print("\n--- Historico de Pagamentos ---")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.nome, COALESCE(p.nome_plano, '-'), pg.valor_pago, pg.data_pagamento, pg.forma_pagamento
        FROM pagamentos pg
        INNER JOIN matriculas m ON pg.id_matricula = m.id_matricula
        INNER JOIN alunos a ON m.id_aluno = a.id_aluno
        LEFT JOIN planos p ON m.id_plano = p.id_plano
        ORDER BY pg.data_pagamento DESC
    """)
    for r in cur.fetchall():
        print(f"{r[0]} | {r[1]} | R$ {r[2]} | {r[3]} | {r[4]}")
    cur.close()
    conn.close()

def consulta_vencendo():
    print("\n--- Matriculas Vencendo em 30 dias ---")
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.nome, a.telefone, p.nome_plano, m.data_fim
        FROM matriculas m
        INNER JOIN alunos a ON m.id_aluno = a.id_aluno
        INNER JOIN planos p ON m.id_plano = p.id_plano
        WHERE m.status = 'ATIVA'
          AND m.data_fim BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
        ORDER BY m.data_fim
    """)
    for r in cur.fetchall():
        print(f"{r[0]} | Tel: {r[1]} | {r[2]} | vence: {r[3]}")
    cur.close()
    conn.close()

def menu_alunos():
    while True:
        print("\n=== ALUNOS ===")
        print("1 - Cadastrar")
        print("2 - Listar")
        print("3 - Buscar")
        print("4 - Atualizar")
        print("5 - Excluir")
        print("0 - Voltar")
        op = input("Opcao: ")
        if op == "1": cadastrar_aluno()
        elif op == "2": listar_alunos()
        elif op == "3": buscar_aluno()
        elif op == "4": atualizar_aluno()
        elif op == "5": excluir_aluno()
        elif op == "0": break

def menu_matriculas():
    while True:
        print("\n=== MATRICULAS ===")
        print("1 - Cadastrar")
        print("2 - Atualizar status")
        print("3 - Excluir")
        print("0 - Voltar")
        op = input("Opcao: ")
        if op == "1": cadastrar_matricula()
        elif op == "2": atualizar_matricula()
        elif op == "3": excluir_matricula()
        elif op == "0": break

def menu_pagamentos():
    while True:
        print("\n=== PAGAMENTOS ===")
        print("1 - Registrar pagamento")
        print("2 - Excluir pagamento")
        print("0 - Voltar")
        op = input("Opcao: ")
        if op == "1": registrar_pagamento()
        elif op == "2": excluir_pagamento()
        elif op == "0": break

def menu_consultas():
    while True:
        print("\n=== CONSULTAS ===")
        print("1 - Matriculas ativas (INNER JOIN)")
        print("2 - Todos os alunos (LEFT JOIN)")
        print("3 - Historico de pagamentos")
        print("4 - Vencendo em 30 dias")
        print("0 - Voltar")
        op = input("Opcao: ")
        if op == "1": consulta_matriculas_ativas()
        elif op == "2": consulta_todos_alunos()
        elif op == "3": consulta_pagamentos()
        elif op == "4": consulta_vencendo()
        elif op == "0": break

def main():
    print("=== SISTEMA DE GESTAO DE ACADEMIA ===")
    if not login():
        print("Acesso negado.")
        return

    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1 - Alunos")
        print("2 - Matriculas")
        print("3 - Pagamentos")
        print("4 - Consultas")
        print("0 - Sair")
        op = input("Opcao: ")
        if op == "1": menu_alunos()
        elif op == "2": menu_matriculas()
        elif op == "3": menu_pagamentos()
        elif op == "4": menu_consultas()
        elif op == "0":
            print("Saindo...")
            break

main()
