# equivalencIA

Sistema de apoio à análise de equivalência e aproveitamento de disciplinas.
O fluxo atual permite cadastrar, buscar e editar alunos, criar e retomar análises,
informar a origem do aproveitamento e selecionar curso e matriz de destino.
Ainda não há funcionalidades de IA ou geração de documentos.

## Tecnologias

- Python e Streamlit para a aplicação.
- PostgreSQL com `psycopg[binary]`, sem ORM.
- `python-dotenv` para carregar as configurações do `.env`.
- `python-docx` como dependência para trabalhar com documentos Word.

## Pré-requisitos

- Python com `pip` e suporte a `venv`. A suíte foi testada com Python 3.12.10;
  outras versões, incluindo 3.14, não foram validadas nesta revisão.
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

### Preparar o banco de dados

Escolha somente o roteiro correspondente ao estado do banco. Execute os comandos
na raiz do projeto e ajuste host, porta, usuário e banco conforme seu `.env`.
`createdb`, `psql` e `pg_dump` precisam estar no PATH. Não coloque senhas nos comandos.

#### Banco novo

Crie o banco e execute o schema atual e o seed, nesta ordem:

```powershell
createdb -h localhost -p 5432 -U postgres equivalencia
psql -h localhost -p 5432 -U postgres -d equivalencia -v ON_ERROR_STOP=1 -f sql/schema.sql
psql -h localhost -p 5432 -U postgres -d equivalencia -v ON_ERROR_STOP=1 -f sql/seed.sql
```

Se o banco vazio já foi criado pelo pgAdmin, dispense o `createdb`.
Prossiga somente se cada comando terminar sem erro. Não execute migrações
incrementais (022 ou 023) em um banco criado com o schema atual.

#### Banco antigo, anterior à separação de aluno (schema do card #021)

Pare o Streamlit. Faça um backup, escolhendo um nome de arquivo ainda não existente:

```powershell
pg_dump -h localhost -p 5432 -U postgres -d equivalencia -Fc -f equivalencia_antes_atualizacao.dump
```

Somente após confirmar o sucesso do backup, execute as duas migrações na ordem:

```powershell
psql -h localhost -p 5432 -U postgres -d equivalencia -v ON_ERROR_STOP=1 -f sql/migrations/022_separar_aluno.sql
psql -h localhost -p 5432 -U postgres -d equivalencia -v ON_ERROR_STOP=1 -f sql/migrations/023_origem_aproveitamento.sql
```

Execute a segunda somente se a primeira terminar com sucesso. Reinicie a aplicação
somente após ambas concluírem. Não reaplique schema ou seed ao banco existente.

#### Banco com a migração 022 já aplicada

Pare a aplicação e faça um backup com `pg_dump`, como acima. Se os campos de origem
ainda estiverem pendentes, execute **somente**:

```powershell
psql -h localhost -p 5432 -U postgres -d equivalencia -v ON_ERROR_STOP=1 -f sql/migrations/023_origem_aproveitamento.sql
```

Após a conclusão com sucesso, reinicie a aplicação. Não repita a migração 022.

#### Banco atualizado

Não reaplique schema, seed ou migrações. As correções de validação, navegação,
mensagens e verificação de atualizações não exigem alteração no banco.

### Iniciar a aplicação

Com o banco preparado pelo roteiro apropriado, execute:

```sh
streamlit run app.py
```

Na interface, use **Testar conexão com o banco** para verificar a conexão.

## Estrutura do projeto

- `app.py`: interface Streamlit.
- `database.py`: conexão e operações de alunos, cursos, matrizes e análises no PostgreSQL.
- `navegacao.py`: etapas e contexto da análise ativa na sessão.
- `pages/`: consulta de cursos e matrizes e páginas do fluxo de análise.
- `services/`: serviços futuros.
- `documents/`: documentos do projeto.
- `sql/`: schema para banco novo, seed e migrações incrementais.
- `.env.example`: modelo de configuração.
- `.gitignore`: arquivos ignorados pelo Git.
- `requirements.txt`: dependências.
- `README.md`: instruções do projeto.

As pastas inicialmente vazias contêm `.gitkeep` para serem preservadas no Git.

## Fluxo de análise — card #021

Nova Análise → Origem do Aproveitamento → Curso e Matriz → Próxima etapa.

As quatro telas mostram a etapa atual e, após a criação/seleção, o nome e o ID
da análise ativa. Em Nova Análise, cadastre/selecione um aluno e crie uma análise,
ou abra **Selecionar uma
análise cadastrada** e clique em **Ativar análise selecionada**. O formulário
passa a editar os dados específicos da análise ativa. Nome e RA são somente
exibidos, sem edição. **Cadastrar outra análise** abre um novo cadastro de análise,
sem excluir a anterior.

**Avançar** salva o formulário da etapa atual antes de navegar. Nova Análise
guarda o **Semestre/Ano de ingresso** do aluno na UNIPAR, no formato `1/2027`
ou `2/2027` (semestre 1 ou 2 e ano com quatro dígitos). O campo continua opcional;
quando preenchido, é validado na tela e antes de qualquer gravação no banco.
Valores antigos são exibidos como estão, sem conversão automática, e precisam
ser corrigidos para o novo formato ao salvar esse formulário. A coluna
`semestre_ano` foi mantida, sem migração de dados. Esse campo não define o
período de encaixe, que pertence a uma etapa posterior à análise curricular.
Origem do Aproveitamento reúne curso de
origem, situação (Concluído, Incompleto ou Trancado) e procedência, vinculados
à análise ativa. O período de encaixe na UNIPAR não é solicitado nessa etapa.
Curso e Matriz guarda a seleção antes de avançar. **Voltar** retorna sem salvar
edições pendentes.

Para atualizar um banco existente para os campos de origem, execute uma vez
`sql/migrations/023_origem_aproveitamento.sql` após `022_separar_aluno.sql`. Em um
banco novo, `sql/schema.sql` já contém a estrutura atual.

O menu lateral continua disponível. Ao visitar Início ou Cursos e Matrizes,
o contexto permanece na sessão; **Continuar análise ativa** no Início retoma
a última etapa visitada. Acesso direto a uma etapa sem análise ativa oferece
um botão para criar/selecionar uma análise.

Todas as páginas do fluxo verificam os pré-requisitos nos dados salvos, inclusive
quando abertas pelo menu lateral. Origem exige uma análise ativa; Curso e Matriz
exige também uma situação de origem salva (Concluído, Incompleto ou Trancado);
Próxima etapa exige ainda curso e matriz salvos. O ingresso continua opcional,
mas um valor preenchido fora do formato precisa ser corrigido na primeira etapa.
RA, curso de origem e procedência não são exigidos para liberar etapas.
Campos apenas preenchidos na tela não liberam o acesso. O bloqueio orienta à
primeira etapa pendente, que também passa a ser o destino de Continuar análise
ativa. As etapas anteriores permanecem acessíveis para consulta e correção.

O contexto (`analise_id`, `aluno_id` e `etapa_atual`, com índice iniciado em zero) existe
somente na sessão Streamlit. Em uma nova sessão ou após recarregar a conexão,
pode ser necessário selecionar novamente a análise. Os dados salvos continuam
no PostgreSQL. A etapa não é persistida no banco.

### Validação manual

1. Execute `streamlit run app.py` com o banco configurado e os scripts SQL
   existentes aplicados. Clique em **Iniciar análise**.
2. Tente **Avançar** sem selecionar aluno: deve aparecer a validação. Abra
   **Cadastrar aluno**, preencha o nome (RA opcional) e clique em **Salvar aluno**.
   O aluno fica salvo independentemente da análise e já aparece selecionado.
   Preencha os dados da análise e avance: deve abrir a etapa 2 com nome e ID.
3. Selecione a situação do curso de origem e avance para Curso e Matriz:
   a análise não deve ser solicitada novamente.
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

## Cadastro independente de aluno — card #022

`aluno` armazena `id`, `nome` obrigatório e `ra` opcional (`NULL` quando vazio).
`analise.aluno_id` é obrigatório e referencia `aluno.id`; várias análises podem
usar o mesmo aluno. Nome e RA não são armazenados na análise: as consultas usam
JOIN. A chave estrangeira impede remover um aluno que possui análises.

Na primeira etapa, **Cadastrar aluno** salva somente o aluno. **Buscar aluno**
permite reutilizar um cadastro existente. **Salvar análise** ou **Avançar** cria
a análise vinculada. Para criar uma segunda análise do mesmo aluno, use
**Cadastrar outra análise**: o aluno permanece selecionado e pode ser substituído
por outro resultado da busca. Semestre/Ano de ingresso, curso de origem, situação de origem
e procedência pertencem à análise.
Nos resultados da busca, **Editar** permite alterar nome e RA pelo ID do aluno.
**Salvar alterações** atualiza o cadastro existente; **Cancelar edição** sai sem salvar.

### Preservação de dados nas migrações

Os roteiros de execução estão em **Preparar o banco de dados**.
No pgAdmin, execute cada arquivo de migração completo; em caso de erro,
execute `ROLLBACK;` antes de corrigir o problema e tentar novamente.

A migração 022 usa uma transação e bloqueia `analise` durante a execução. Preserva
IDs, datas, dados da análise e vínculos de curso/matriz. Cada análise antiga
recebe um aluno próprio: nome e RA não são identificadores suficientes para
unificar pessoas com segurança. RAs antigos vazios são convertidos em `NULL`;
nomes e RAs preenchidos são copiados. Nomes sem nenhum caractere não branco
fazem a migração falhar e reverter todas as alterações: corrija esses registros
no schema antigo antes de tentar novamente.

As colunas antigas `analise.nome_aluno` e `analise.ra` são removidas somente após
a cópia e o vínculo obrigatório. Nenhuma análise é excluída. Isso torna o banco
incompatível com a versão anterior da aplicação; não volte apenas o código.
Se precisar reverter, restaure o backup em um banco separado para conferência
e use o código correspondente ao #021. Não há migração reversa automática.
O script não é idempotente: uma segunda execução falha sem apagar os dados.

### Verificar o relacionamento

Cadastre um aluno com RA e outro somente com nome. Tente também salvar nome
vazio: deve ser impedido. Crie duas análises selecionando o mesmo aluno e confira
no Query Tool/psql:

```sql
SELECT a.id AS analise_id, a.aluno_id, al.nome, al.ra
FROM analise a
JOIN aluno al ON al.id = a.aluno_id
ORDER BY a.aluno_id, a.id;

SELECT aluno_id, count(*) AS quantidade_analises
FROM analise
GROUP BY aluno_id
HAVING count(*) > 1;
```

As duas análises devem mostrar o mesmo `aluno_id`. Complete também o roteiro
de navegação acima, verificando o retorno dos dados salvos.

### Testes

Interface com AppTest e persistência simulada, mais validação de nome:

```powershell
python -m unittest discover -s tests -v
```

Para incluir testes reais de PostgreSQL (conexão do `.env`, usuário com permissão
de criar schemas), execute no PowerShell:

```powershell
$env:TEST_POSTGRES = '1'
python -m unittest discover -s tests -v
Remove-Item Env:TEST_POSTGRES
```

Os testes de integração usam schemas exclusivos dentro de transações revertidas
ao final; não migram as tabelas da aplicação. Cobrem schema novo, RA opcional,
nome obrigatório, chaves estrangeiras, duas análises do mesmo aluno, preservação
dos dados legados e rollback da migração inválida. Sem a variável, são ignorados.

Limitações: RA não tem unicidade e não há unificação automática de cadastros
legados. Edição direta de aluno e campos de origem estão implementados.
O contexto de navegação continua limitado à sessão Streamlit.

## Busca de alunos — card #023

Em Nova Análise, digite o nome completo ou parte dele em **Buscar aluno** e
pressione Enter ou saia do campo. A consulta usa `ILIKE` com parâmetro para
buscar o trecho em qualquer posição, sem diferenciar maiúsculas/minúsculas.
Espaços nas extremidades são ignorados; busca vazia não consulta nem lista todos
os alunos. `%`, `_` e `!` digitados são tratados como caracteres literais.

Cada resultado apresenta nome, RA (ou **RA não informado**), número do cadastro
e **Selecionar**. O vínculo usa sempre o ID, inclusive quando há nomes iguais.
Se não houver correspondências, aparece **Nenhum aluno encontrado.**

A seleção fica em `st.session_state.aluno_id` e é exibida abaixo da busca.
Alterar ou limpar o texto de busca não troca o aluno selecionado: use outro
botão **Selecionar** ou **Limpar seleção**. **Salvar análise** e **Avançar** usam
esse aluno, sem outro combo. Cadastrar um aluno novo também o seleciona.
Uma análise ativa mantém seu próprio aluno; para iniciar outra, use
**Cadastrar outra análise**. A seleção de análises existentes permanece disponível.

### Testar manualmente a busca

1. Com o banco preparado conforme o roteiro da versão atual, execute
   `streamlit run app.py` e entre em Nova Análise.
2. Cadastre dois alunos com nomes contendo **Matheus**, um com RA e outro sem.
3. Pesquise nome completo, depois `theus` e `mAtHeUs`. Confira os resultados,
   seus IDs e a apresentação do RA.
4. Pesquise um nome inexistente e confira a mensagem de nenhum resultado.
5. Selecione um resultado e avance. Volte e confira o mesmo aluno e análise.
6. Use **Cadastrar outra análise**, pesquise e selecione outro aluno. Se houver
   homônimos, confira o número do cadastro para selecionar o registro correto.
7. Selecione um aluno, visite Início e retorne. Ele deve continuar selecionado.
   Use **Limpar seleção** e tente avançar: deve solicitar cadastro ou seleção.

Os comandos de teste documentados acima incluem busca real no PostgreSQL e
testes de interface para homônimos, RA ausente, nenhum resultado, seleção por
ID e regressão dos cards #021/#022. Os testes reais continuam isolados e com rollback.

Limitações da busca: não remove acentos, não pesquisa RA e ainda não tem
paginação ou índice específico para substring. Termos muito amplos podem
produzir muitos resultados. A edição direta está disponível pelo botão **Editar**.
