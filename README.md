## Academia FitLife

**Aluno:** Erick Ruan Nunes Vieira  
**Disciplina:** Banco de Dados  
**Professor:** Anderson Costa

## Sobre o projeto

Sistema desktop para gerenciar alunos, planos, matrículas e pagamentos de uma
academia. O projeto evolui um CRUD anterior com interface gráfica e recursos
do PostgreSQL usados para organizar consultas, calcular valores e registrar
pagamentos.

## Tecnologias

Python, Tkinter, psycopg2, PostgreSQL e pgAdmin.

## Funcionalidades

- Login e criação de conta.
- Cadastro, busca, edição e exclusão de alunos.
- Criação e gerenciamento de matrículas.
- Registro e histórico de pagamentos.
- Relatórios de matrículas, vencimentos e total pago por aluno.

## Banco de dados

**SGBD:** PostgreSQL.

**Tabelas principais:** usuarios, alunos, planos, matriculas e pagamentos.
As matrículas relacionam alunos e planos; os pagamentos pertencem às matrículas.

| Recurso | Finalidade | Uso na aplicação |
|---|---|---|
| View: vw_matriculas_alunos | Reunir aluno, plano e situação da matrícula | Listagem de matrículas |
| Function: fn_total_pago_aluno | Receber o ID do aluno e retornar o total pago | Consulta na aba Relatórios |
| Procedure: pr_registrar_pagamento | Validar matrícula, valor e forma antes de gravar | Registro na aba Pagamentos |

Os três recursos são chamados pelo Python e utilizados efetivamente pela interface.

## Como executar

1. Instale Python com Tkinter e PostgreSQL.
2. No pgAdmin, crie um banco chamado **academia**.
3. No Query Tool desse banco, execute os arquivos nesta ordem:

```text
Banco_de_dados/ddl/criar_tabelas.sql
Banco_de_dados/dml/dados.sql
Banco_de_dados/ddl/view.sql
Banco_de_dados/ddl/function.sql
Banco_de_dados/ddl/procedure.sql
```

Se o banco já estiver preparado, não repita os scripts de tabelas e dados.
O arquivo dados.sql já cadastra os planos; não é necessário executar planos.sql.

4. Confira a conexão em projeto/src/conexao.py. No ambiente de desenvolvimento:
   **127.0.0.1**, porta **5433**, banco **academia**, usuário **postgres**.
5. Na pasta principal do projeto, instale a dependência e execute:

```powershell
python -m pip install psycopg2-binary
python projeto/src/main.py
```

A senha do PostgreSQL é solicitada em uma janela e mantida somente na memória.
Para entrar no sistema, crie uma conta ou use **admin / admin123**, dos dados iniciais.

## Organização

- **Banco_de_dados/**: scripts SQL e diagrama.
- **projeto/src/**: interface, conexão e operações em Python.
- **docs/**: portfólio do projeto.

## Portfólio

O projeto demonstra modelagem relacional, consultas com JOIN, rotinas SQL
e integração entre aplicação e banco de dados. Foi desenvolvido com auxílio
de IA, com estudo e testes manuais do autor.

[Portfólio em PDF](docs/Portfolio_Banco_de_Dados.pdf)

**Repositório:** https://github.com/erickruannv/academia-bd  
## Vídeo explicativo

Demonstração do sistema e dos recursos de banco de dados: View, Function e Procedure.

**Link do vídeo:** https://youtu.be/iFHY-ydyVSM
