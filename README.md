# 🏋️ Academia FitLife — Sistema de Gestão

> Trabalho Acadêmico — Disciplina: Banco de Dados  
> Tema: Gestão de Academia (alunos, planos, matrículas e pagamentos)

---

## 📋 Descrição

Sistema desktop desenvolvido em **Python com Tkinter** para gerenciar o cadastro de alunos, planos de assinatura, matrículas e pagamentos de uma academia. O sistema conta com tela de login, interface gráfica completa e integração com banco de dados **PostgreSQL**.

---

## 🗂️ Estrutura do Repositório

```
academia-bd/
├── diagrama/
│   └── der_academia.png        # Diagrama Entidade-Relacionamento
├── ddl/
│   └── criar_tabelas.sql       # Criação das tabelas e restrições
├── dml/
│   └── dados.sql               # Inserção, atualização e deleção de dados
├── dql/
│   └── consultas.sql           # Consultas com JOINs, filtros e ordenação
├── src/
│   └── main.py                 # Código-fonte da aplicação (Python + Tkinter)
└── README.md
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.10+ | Linguagem principal |
| Tkinter | (nativo) | Interface gráfica |
| psycopg2 | 2.9+ | Conector PostgreSQL |
| PostgreSQL | 15+ | Banco de dados relacional |

---

## 🗄️ Modelo de Dados

O banco é composto por **5 tabelas** relacionadas:

| Tabela | Descrição |
|---|---|
| `usuarios` | Usuários do sistema (autenticação) |
| `alunos` | Alunos cadastrados na academia |
| `planos` | Planos de assinatura disponíveis |
| `matriculas` | Vínculo entre aluno e plano |
| `pagamentos` | Registro de pagamentos das matrículas |

---

## 🖥️ Funcionalidades

### Autenticação
- Tela de login com validação no banco de dados

### Gerenciamento de Alunos (CRUD completo)
- Cadastrar novo aluno
- Listar todos os alunos (com ordenação e filtro por nome/CPF)
- Atualizar dados de um aluno
- Excluir aluno (com exclusão em cascata das matrículas e pagamentos)

### Gerenciamento de Matrículas
- Criar nova matrícula vinculando aluno a um plano
- Filtrar matrículas por status (ATIVA / CANCELADA / VENCIDA)
- Atualizar status da matrícula
- Remover matrícula

### Pagamentos
- Registrar pagamento vinculado a uma matrícula ativa
- Selecionar forma de pagamento (PIX / CARTÃO / DINHEIRO)
- Visualizar histórico de pagamentos

### Relatórios (Consultas com JOIN)
- **Matrículas ativas** — usa `INNER JOIN` entre alunos, matrículas e planos
- **Todos os alunos** — usa `LEFT JOIN` (inclui alunos sem matrícula)
- **Histórico de pagamentos** — usa `INNER JOIN + LEFT JOIN`
- **Vencendo em 30 dias** — usa `INNER JOIN` com filtro `BETWEEN`

---

## ⚙️ Como Executar

### 1. Pré-requisitos

- Python 3.10 ou superior
- PostgreSQL 15 instalado e em execução
- pip

### 2. Instalar dependências Python

```bash
pip install psycopg2-binary
```

### 3. Criar o banco de dados

No `psql` (ou pgAdmin), execute:

```sql
CREATE DATABASE academia;
```

### 4. Criar as tabelas

```bash
psql -U postgres -d academia -f ddl/criar_tabelas.sql
```

### 5. Inserir dados iniciais

```bash
psql -U postgres -d academia -f dml/dados.sql
```

### 6. Configurar a conexão (se necessário)

Abra o arquivo `src/main.py` e ajuste as configurações de conexão no início do arquivo:

```python
DB_CONFIG = {
    "host":     "localhost",
    "database": "academia",
    "user":     "postgres",
    "password": "root"       # <- altere para sua senha
}
```

### 7. Executar a aplicação

```bash
python src/main.py
```

### Login padrão

| Campo | Valor |
|---|---|
| Usuário | `admin` |
| Senha | `admin123` |

---

## 🔍 Exemplos de Consultas SQL

### INNER JOIN — Matrículas ativas

```sql
SELECT a.nome, p.nome_plano, m.data_inicio, m.data_fim, m.status
FROM matriculas m
INNER JOIN alunos a ON m.id_aluno = a.id_aluno
INNER JOIN planos p ON m.id_plano = p.id_plano
WHERE m.status = 'ATIVA'
ORDER BY a.nome;
```

### LEFT JOIN — Todos os alunos (com ou sem matrícula)

```sql
SELECT a.nome, a.email,
       COALESCE(p.nome_plano, 'Sem plano') AS plano,
       COALESCE(m.status, '—')             AS status
FROM alunos a
LEFT JOIN matriculas m ON a.id_aluno = m.id_aluno
LEFT JOIN planos p     ON m.id_plano = p.id_plano
ORDER BY a.nome;
```

---

## 🎬 Vídeo Demonstrativo

> Link: https://youtu.be/cmB5e1HSQ58

---

## 👤 Autor

**Erick Ruan Nunes Vieira**  
Disciplina: Banco de Dados — Prof. Anderson Costa  
