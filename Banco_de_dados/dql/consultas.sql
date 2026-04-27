SELECT
    a.nome            AS aluno,
    p.nome_plano      AS plano,
    m.data_inicio,
    m.data_fim,
    m.status
FROM matriculas m
INNER JOIN alunos a  ON m.id_aluno  = a.id_aluno
INNER JOIN planos p  ON m.id_plano  = p.id_plano
WHERE m.status = 'ATIVA'
ORDER BY a.nome;
SELECT
    a.nome              AS aluno,
    p.nome_plano        AS plano,
    pg.valor_pago,
    pg.data_pagamento,
    pg.forma_pagamento
FROM pagamentos pg
INNER JOIN matriculas m ON pg.id_matricula = m.id_matricula
INNER JOIN alunos a     ON m.id_aluno      = a.id_aluno
INNER JOIN planos p     ON m.id_plano      = p.id_plano
ORDER BY pg.data_pagamento DESC;
SELECT
    a.nome,
    a.email,
    m.status          AS status_matricula,
    p.nome_plano      AS plano
FROM alunos a
LEFT JOIN matriculas m ON a.id_aluno = m.id_aluno
LEFT JOIN planos p     ON m.id_plano = p.id_plano
ORDER BY a.nome;
SELECT
    a.id_aluno,
    a.nome,
    a.email
FROM alunos a
LEFT JOIN matriculas m ON a.id_aluno = m.id_aluno
WHERE m.id_matricula IS NULL;
SELECT * FROM alunos
WHERE nome ILIKE '%carlos%'
ORDER BY nome ASC;
SELECT * FROM matriculas
WHERE status = 'ATIVA'
ORDER BY data_inicio DESC;
SELECT * FROM pagamentos
WHERE valor_pago > 200.00
ORDER BY valor_pago DESC;
SELECT
    forma_pagamento,
    COUNT(*)          AS quantidade,
    SUM(valor_pago)   AS total
FROM pagamentos
GROUP BY forma_pagamento
ORDER BY total DESC;
SELECT
    a.nome,
    a.telefone,
    p.nome_plano,
    m.data_fim
FROM matriculas m
INNER JOIN alunos a ON m.id_aluno = a.id_aluno
INNER JOIN planos p ON m.id_plano = p.id_plano
WHERE m.status = 'ATIVA'
  AND m.data_fim BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY m.data_fim ASC;
