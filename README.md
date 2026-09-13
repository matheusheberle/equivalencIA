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
- `database.py`: conexão e teste do PostgreSQL.
- `pages/`: páginas futuras.
- `services/`: serviços futuros.
- `documents/`: documentos do projeto.
- `sql/`: scripts SQL futuros.
- `.env.example`: modelo de configuração.
- `.gitignore`: arquivos ignorados pelo Git.
- `requirements.txt`: dependências.
- `README.md`: instruções do projeto.

As pastas inicialmente vazias contêm `.gitkeep` para serem preservadas no Git.
