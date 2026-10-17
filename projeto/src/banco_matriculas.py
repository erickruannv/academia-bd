from banco import consultar as _consultar, transacao as _transacao

SITUACOES = ("ATIVA", "CANCELADA", "VENCIDA")

# Regra de negocio violada (aluno com outra matricula ATIVA, registro inexistente etc.);
# a mensagem ja e a que deve ser mostrada ao usuario
class MatriculaInvalida(Exception):
    pass

def listar_matriculas():
    return _consultar("""
        SELECT id_matricula, aluno, plano, status, data_inicio, data_fim
        FROM vw_matriculas_alunos
        ORDER BY aluno, data_inicio DESC
    """)

def listar_alunos():
    # CPF ajuda a diferenciar alunos com o mesmo nome na selecao
    return _consultar("SELECT id_aluno, nome, cpf FROM alunos ORDER BY nome")

def listar_planos():
    return _consultar("SELECT id_plano, nome_plano, valor, duracao_meses FROM planos ORDER BY duracao_meses, nome_plano")

def _travar_aluno(cur, id_aluno):
    # Bloqueia a linha do aluno ate o fim da transacao: duas sessoes criando ou ativando
    # matriculas do mesmo aluno passam pela verificacao uma de cada vez
    cur.execute("SELECT 1 FROM alunos WHERE id_aluno = %s FOR UPDATE", (id_aluno,))
    if cur.fetchone() is None:
        raise MatriculaInvalida("Este aluno nao existe mais.")

def _verificar_sem_ativa(cur, id_aluno, ignorar_matricula=None):
    cur.execute("""
        SELECT 1 FROM matriculas
        WHERE id_aluno = %s AND status = 'ATIVA' AND id_matricula IS DISTINCT FROM %s
    """, (id_aluno, ignorar_matricula))
    if cur.fetchone() is not None:
        raise MatriculaInvalida("Este aluno ja possui uma matricula ATIVA. "
                                "Cancele ou marque a atual como vencida antes.")

def cadastrar_matricula(id_aluno, id_plano):
    # data_inicio = hoje e data_fim = hoje + duracao do plano, calculadas no PostgreSQL
    def operacao(cur):
        _travar_aluno(cur, id_aluno)
        _verificar_sem_ativa(cur, id_aluno)
        cur.execute("""
            INSERT INTO matriculas (id_aluno, id_plano, data_inicio, data_fim, status)
            SELECT %s, id_plano, CURRENT_DATE,
                   (CURRENT_DATE + duracao_meses * INTERVAL '1 month')::DATE, 'ATIVA'
            FROM planos
            WHERE id_plano = %s
            RETURNING id_matricula
        """, (id_aluno, id_plano))
        linha = cur.fetchone()
        if linha is None:
            raise MatriculaInvalida("Este plano nao existe mais.")
        return linha[0]
    return _transacao(operacao)

def alterar_situacao(id_matricula, status):
    if status not in SITUACOES:
        raise MatriculaInvalida("Situacao invalida.")
    def operacao(cur):
        cur.execute("SELECT id_aluno FROM matriculas WHERE id_matricula = %s", (id_matricula,))
        linha = cur.fetchone()
        if linha is None:
            raise MatriculaInvalida("Esta matricula nao existe mais.")
        id_aluno = linha[0]
        # Mesma ordem de bloqueio do cadastro (aluno, depois matricula)
        _travar_aluno(cur, id_aluno)
        cur.execute("SELECT 1 FROM matriculas WHERE id_matricula = %s FOR UPDATE", (id_matricula,))
        if cur.fetchone() is None:
            raise MatriculaInvalida("Esta matricula nao existe mais.")
        if status == "ATIVA":
            _verificar_sem_ativa(cur, id_aluno, id_matricula)
        cur.execute("UPDATE matriculas SET status = %s WHERE id_matricula = %s", (status, id_matricula))
    _transacao(operacao)

def contar_pagamentos(id_matricula):
    return _consultar("SELECT COUNT(*) FROM pagamentos WHERE id_matricula = %s", (id_matricula,))[0][0]

def excluir_matricula(id_matricula):
    # Pagamentos da matricula saem junto pelo ON DELETE CASCADE.
    # Retorna False se a matricula ja tinha sido excluida
    def operacao(cur):
        cur.execute("DELETE FROM matriculas WHERE id_matricula = %s", (id_matricula,))
        return cur.rowcount > 0
    return _transacao(operacao)
