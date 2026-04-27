INSERT INTO usuarios (login, senha) VALUES ('admin', 'admin123');
INSERT INTO planos (nome_plano, valor, duracao_meses) VALUES
    ('Mensal',      89.90,   1),
    ('Trimestral', 239.90,   3),
    ('Semestral',  419.90,   6),
    ('Anual',      749.90,  12);
INSERT INTO alunos (nome, cpf, telefone, email) VALUES
    ('Carlos Henrique Souza',  '01234567890', '(86) 99101-2233', 'carlos.h@gmail.com'),
    ('Fernanda Lima Rocha',    '09876543210', '(86) 98877-6655', 'fernanda.lima@hotmail.com'),
    ('João Pedro Alves',       '11122233344', '(86) 99988-7766', 'joaopedro@gmail.com'),
    ('Mariana Costa',          '55566677788', '(86) 99012-3456', 'mariana.costa@yahoo.com'),
    ('Ricardo Batista',        '33344455566', '(86) 98765-4321', 'ricbatista@gmail.com');
INSERT INTO matriculas (id_aluno, id_plano, data_inicio, data_fim, status) VALUES
    (1, 2, '2025-01-10', '2025-04-10', 'VENCIDA'),
    (2, 4, '2025-03-01', '2026-03-01', 'ATIVA'),
    (3, 1, '2025-04-01', '2025-05-01', 'ATIVA'),
    (4, 3, '2025-02-15', '2025-08-15', 'ATIVA'),
    (5, 1, '2025-03-20', '2025-04-20', 'CANCELADA');
INSERT INTO pagamentos (id_matricula, valor_pago, data_pagamento, forma_pagamento) VALUES
    (1, 239.90, '2025-01-10', 'PIX'),
    (2, 749.90, '2025-03-01', 'CARTAO'),
    (3,  89.90, '2025-04-01', 'DINHEIRO'),
    (4, 419.90, '2025-02-15', 'PIX'),
    (5,  89.90, '2025-03-20', 'DINHEIRO');
UPDATE alunos
SET telefone = '(86) 99111-2222'
WHERE id_aluno = 1;
UPDATE matriculas
SET status = 'CANCELADA'
WHERE status = 'VENCIDA';
UPDATE planos
SET valor = 99.90
WHERE nome_plano = 'Mensal';
