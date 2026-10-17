from banco import consultar, transacao

FORMAS = ("PIX", "CARTAO", "DINHEIRO")

def listar_pagamentos():
    # Historico de pagamentos (consulta do sistema antigo), do mais recente para o mais antigo
    return consultar("""
        SELECT pg.id_pagamento, a.nome, COALESCE(p.nome_plano, '-'), pg.valor_pago,
               pg.forma_pagamento, pg.data_pagamento
        FROM pagamentos pg
        INNER JOIN matriculas m ON pg.id_matricula = m.id_matricula
        INNER JOIN alunos a ON m.id_aluno = a.id_aluno
        LEFT JOIN planos p ON m.id_plano = p.id_plano
        ORDER BY pg.data_pagamento DESC, pg.id_pagamento DESC
    """)

def listar_matriculas_ativas():
    # So matriculas ATIVAS podem receber pagamento; o CPF diferencia alunos com o mesmo nome
    return consultar("""
        SELECT m.id_matricula, a.nome, a.cpf, p.nome_plano
        FROM matriculas m
        INNER JOIN alunos a ON m.id_aluno = a.id_aluno
        INNER JOIN planos p ON m.id_plano = p.id_plano
        WHERE m.status = 'ATIVA'
        ORDER BY a.nome, m.id_matricula
    """)

def registrar_pagamento(id_matricula, valor, forma):
    # As regras (matricula ATIVA, valor positivo, forma valida) ficam na Procedure
    transacao(lambda cur: cur.execute("CALL pr_registrar_pagamento(%s, %s, %s)", (id_matricula, valor, forma)))

def excluir_pagamento(id_pagamento):
    # Retorna False se o pagamento ja tinha sido excluido
    def operacao(cur):
        cur.execute("DELETE FROM pagamentos WHERE id_pagamento = %s", (id_pagamento,))
        return cur.rowcount > 0
    return transacao(operacao)
