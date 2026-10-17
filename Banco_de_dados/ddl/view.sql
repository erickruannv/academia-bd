CREATE OR REPLACE VIEW vw_matriculas_alunos AS
SELECT
    a.nome AS aluno,
    p.nome_plano AS plano,
    m.status,
    m.id_matricula,
    m.data_inicio,
    m.data_fim
FROM matriculas AS m
INNER JOIN alunos AS a
    ON m.id_aluno = a.id_aluno
INNER JOIN planos AS p
    ON m.id_plano = p.id_plano;