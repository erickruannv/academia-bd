CREATE OR REPLACE FUNCTION fn_total_pago_aluno(p_id_aluno INTEGER)
RETURNS NUMERIC
LANGUAGE sql
AS $$
    SELECT COALESCE(SUM(pg.valor_pago), 0)
    FROM pagamentos pg
    JOIN matriculas m
        ON m.id_matricula = pg.id_matricula
    WHERE m.id_aluno = p_id_aluno;
$$;
