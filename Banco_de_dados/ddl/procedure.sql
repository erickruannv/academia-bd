CREATE OR REPLACE PROCEDURE pr_registrar_pagamento(
    p_matricula INTEGER,
    p_valor NUMERIC,
    p_forma VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_status VARCHAR;
BEGIN
    SELECT status INTO v_status
    FROM matriculas
    WHERE id_matricula = p_matricula
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Matrícula não encontrada.';
    END IF;

    IF v_status IS DISTINCT FROM 'ATIVA' THEN
        RAISE EXCEPTION 'A matrícula precisa estar ATIVA.';
    END IF;

    IF p_valor IS NULL OR p_valor <= 0
       OR p_valor::TEXT IN ('NaN', 'Infinity', '-Infinity') THEN
        RAISE EXCEPTION 'Informe um valor positivo e válido.';
    END IF;

    IF p_forma IS NULL
       OR p_forma NOT IN ('PIX', 'CARTAO', 'DINHEIRO') THEN
        RAISE EXCEPTION 'Forma de pagamento inválida.';
    END IF;

    INSERT INTO pagamentos (
        id_matricula, valor_pago, forma_pagamento
    )
    VALUES (p_matricula, p_valor, p_forma);
END;
$$;

