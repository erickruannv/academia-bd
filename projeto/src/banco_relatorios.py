from banco import consultar

def listar_alunos():
    # Para a selecao do total pago; o CPF diferencia alunos com o mesmo nome
    return consultar("SELECT id_aluno, nome, cpf FROM alunos ORDER BY nome, cpf")

def total_pago_aluno(id_aluno):
    # O calculo e feito pela Function no PostgreSQL
    return consultar("SELECT fn_total_pago_aluno(%s)", (id_aluno,))[0][0]

def matriculas_ativas():
    return consultar("""
        SELECT aluno, plano, data_inicio, data_fim
        FROM vw_matriculas_alunos
        WHERE status = 'ATIVA'
        ORDER BY aluno
    """)

def todos_alunos():
    # LEFT JOIN: alunos sem matricula aparecem com "Sem plano"
    return consultar("""
        SELECT a.nome, a.cpf, a.email,
               COALESCE(p.nome_plano, 'Sem plano') AS plano,
               COALESCE(m.status, '-') AS status
        FROM alunos a
        LEFT JOIN matriculas m ON a.id_aluno = m.id_aluno
        LEFT JOIN planos p ON m.id_plano = p.id_plano
        ORDER BY a.nome, a.cpf, m.data_inicio DESC
    """)

def vencendo_30_dias():
    # Matriculas ATIVAS que vencem de hoje ate daqui a 30 dias (inclusive)
    return consultar("""
        SELECT a.nome, a.telefone, p.nome_plano, m.data_fim, m.data_fim - CURRENT_DATE AS dias
        FROM matriculas m
        INNER JOIN alunos a ON m.id_aluno = a.id_aluno
        INNER JOIN planos p ON m.id_plano = p.id_plano
        WHERE m.status = 'ATIVA'
          AND m.data_fim BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
        ORDER BY m.data_fim, a.nome
    """)
