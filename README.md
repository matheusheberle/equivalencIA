# equivalencIA

Sistema de apoio à análise de equivalência e aproveitamento de disciplinas.
A estrutura inicial oferece uma interface Streamlit com teste de conexão ao
PostgreSQL. Ainda não há funcionalidades de IA.

## Tecnologias

- Python e Streamlit para a aplicação.
- PostgreSQL com `psycopg[binary]`, sem ORM.
- `python-dotenv` para carregar as configurações do `.env`.
- `python-docx` como dependência para trabalhar com documentos Word.

## Pré-requisitos

- Python com `pip` e suporte a `venv` (o ambiente atual utiliza Python 3.14).
- PostgreSQL instalado e em execução, com um banco chamado `equivalencia`
  e um usuário com permissão de conexão. A aplicação não cria o banco;
  ele deve existir antes do teste de conexão.

## Configuração e execução

Na pasta do projeto, crie o ambiente virtual:

```sh
python -m venv .venv
```

Ative no Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Ou no Linux/macOS:

```sh
source .venv/bin/activate
```

Instale as dependências:

```sh
python -m pip install -r requirements.txt
```

Se ainda não houver um `.env`, copie o exemplo no Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

Ou no Linux/macOS:

```sh
cp .env.example .env
```

Edite o `.env` com os dados do seu PostgreSQL:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=equivalencia
DB_USER=postgres
DB_PASSWORD=sua_senha
```

O `.env` contém credenciais e não deve ser enviado ao repositório. Ele está
incluído no `.gitignore`; versione apenas o `.env.example`, sem senhas reais.

Execute a aplicação:

```sh
streamlit run app.py
```

Na interface, use **Testar conexão com o banco** para verificar a conexão.

## Estrutura inicial

- `app.py`: interface Streamlit.
- `database.py`: conexão e operações de cursos, matrizes e análises no PostgreSQL.
- `navegacao.py`: etapas e contexto da análise ativa na sessão.
- `pages/`: consulta de cursos e matrizes e páginas do fluxo de análise.
- `services/`: serviços futuros.
- `documents/`: documentos do projeto.
- `sql/`: scripts SQL futuros.
- `.env.example`: modelo de configuração.
- `.gitignore`: arquivos ignorados pelo Git.
- `requirements.txt`: dependências.
- `README.md`: instruções do projeto.

As pastas inicialmente vazias contêm `.gitkeep` para serem preservadas no Git.

## Fluxo de análise — card #021

Nova Análise → Origem do Aproveitamento → Curso e Matriz → Próxima etapa.

As quatro telas mostram a etapa atual e, após a criação/seleção, o nome e o ID
da análise ativa. Em Nova Análise, crie uma análise ou abra **Selecionar uma
análise cadastrada** e clique em **Ativar análise selecionada**. O formulário
passa a editar a análise ativa. **Cadastrar outra análise** abre um novo cadastro,
sem excluir a anterior.

**Avançar** salva o formulário de Nova Análise ou a seleção de Curso e Matriz
antes de navegar. **Voltar** recupera os dados já salvos, sem salvar edições
pendentes. O primeiro Voltar e o último Avançar ficam desabilitados.
Origem do Aproveitamento e Próxima etapa são telas provisórias; os campos
Situação e Procedência permanecem no formulário original.

O menu lateral continua disponível. Ao visitar Início ou Cursos e Matrizes,
o contexto permanece na sessão; **Continuar análise ativa** no Início retoma
a última etapa visitada. Acesso direto a uma etapa sem análise ativa oferece
um botão para criar/selecionar uma análise.

O contexto (`analise_id` e `etapa_atual`, com índice iniciado em zero) existe
somente na sessão Streamlit. Em uma nova sessão ou após recarregar a conexão,
pode ser necessário selecionar novamente a análise. Os dados salvos continuam
no PostgreSQL. Não há alteração de esquema nem persistência da etapa no banco.

### Validação manual

1. Execute `streamlit run app.py` com o banco configurado e os scripts SQL
   existentes aplicados. Clique em **Iniciar análise**.
2. Tente **Avançar** sem nome: deve aparecer a validação. Preencha os campos
   e avance: deve abrir a etapa 2, com nome e ID da análise criada.
3. Avance para Curso e Matriz: a análise não deve ser solicitada novamente.
   Sem selecionar matriz, Avançar deve mostrar a validação. Selecione uma
   matriz e avance para a mensagem de próxima etapa ainda não implementada.
4. Volte até Nova Análise e confira os dados salvos e o mesmo ID. Altere um
   campo e avance novamente: deve atualizar a análise, sem criar uma duplicata.
5. Visite Início e use **Continuar análise ativa**. Visite também Cursos e
   Matrizes pelo menu e confira que o contexto continua ao retornar.
6. Em Nova Análise, ative outra análise cadastrada e confira os dados e a
   seleção de curso/matriz próprios dela. Teste **Cadastrar outra análise**.
7. Em uma nova sessão, entre diretamente em Curso e Matriz: deve receber
   orientação para criar/selecionar uma análise, sem erro.

Os testes de interface usam AppTest e persistência simulada, sem acessar o
PostgreSQL. Execute: `python -m unittest discover -s tests -v`.
