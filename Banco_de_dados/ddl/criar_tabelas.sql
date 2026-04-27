
CREATE TABLE usuarios (
    id_usuario   SERIAL PRIMARY KEY,
    login        VARCHAR(50) UNIQUE NOT NULL,
    senha        VARCHAR(100) NOT NULL,
    criado_em    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE planos (
    id_plano        SERIAL PRIMARY KEY,
    nome_plano      VARCHAR(50) UNIQUE NOT NULL,
    valor           DECIMAL(10,2) NOT NULL CHECK (valor > 0),
    duracao_meses   INT NOT NULL CHECK (duracao_meses > 0)
);

CREATE TABLE alunos (
    id_aluno      SERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    cpf           VARCHAR(11) UNIQUE NOT NULL,
    telefone      VARCHAR(20),
    email         VARCHAR(100) UNIQUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE matriculas (
    id_matricula  SERIAL PRIMARY KEY,
    id_aluno      INT NOT NULL,
    id_plano      INT NOT NULL,
    data_inicio   DATE DEFAULT CURRENT_DATE,
    data_fim      DATE,
    status        VARCHAR(20) DEFAULT 'ATIVA',

    CONSTRAINT fk_matricula_aluno
        FOREIGN KEY (id_aluno) REFERENCES alunos(id_aluno)
        ON DELETE CASCADE,

    CONSTRAINT fk_matricula_plano
        FOREIGN KEY (id_plano) REFERENCES planos(id_plano)
        ON DELETE RESTRICT,

    CONSTRAINT chk_status_matricula
        CHECK (status IN ('ATIVA', 'CANCELADA', 'VENCIDA'))
);

CREATE TABLE pagamentos (
    id_pagamento    SERIAL PRIMARY KEY,
    id_matricula    INT NOT NULL,
    valor_pago      DECIMAL(10,2) NOT NULL CHECK (valor_pago > 0),
    data_pagamento  DATE DEFAULT CURRENT_DATE,
    forma_pagamento VARCHAR(30),

    CONSTRAINT fk_pagamento_matricula
        FOREIGN KEY (id_matricula) REFERENCES matriculas(id_matricula)
        ON DELETE CASCADE
);
