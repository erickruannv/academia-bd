from conexao import conectar

# Rotinas comuns aos modulos banco_*.py: abrem a conexao com conectar() (senha em memoria)
# e sempre fecham cursor e conexao

def consultar(sql, parametros=()):
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

def transacao(operacao):
    # Executa operacao(cur) numa unica transacao: commit no fim, rollback em qualquer erro
    conn = conectar()
    try:
        cur = conn.cursor()
        try:
            resultado = operacao(cur)
            conn.commit()
            return resultado
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
    finally:
        conn.close()
