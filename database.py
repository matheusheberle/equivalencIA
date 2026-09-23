import os
import re

import psycopg
from dotenv import load_dotenv

load_dotenv()


def obter_conexao():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def testar_conexao():
    try:
        with obter_conexao() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()

        return True, "Conexão com PostgreSQL realizada com sucesso."

    except psycopg.Error as erro:
        return False, f"Erro ao conectar com o PostgreSQL: {erro}"


def listar_cursos():
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT id, codigo, nome
                FROM curso
                ORDER BY nome;
            """)
            return cursor.fetchall()


def listar_matrizes_por_curso(curso_id):
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT id, curso_id, codigo
                FROM matriz
                WHERE curso_id = %s
                ORDER BY codigo;
            """, (curso_id,))
            return cursor.fetchall()


def _normalizar_dados_aluno(nome, ra):
    nome = (nome or "").strip()
    if not nome:
        raise ValueError("O nome do aluno é obrigatório.")
    ra = (ra or "").strip() or None
    return nome, ra


def criar_aluno(nome, ra=None):
    nome, ra = _normalizar_dados_aluno(nome, ra)
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO aluno (nome, ra) VALUES (%s, %s) RETURNING id;",
                (nome, ra),
            )
            return cursor.fetchone()[0]


def atualizar_aluno(aluno_id, nome, ra=None):
    nome, ra = _normalizar_dados_aluno(nome, ra)
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "UPDATE aluno SET nome = %s, ra = %s WHERE id = %s RETURNING id;",
                (nome, ra, aluno_id),
            )
            return cursor.fetchone() is not None


def obter_aluno(aluno_id):
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id, nome, ra FROM aluno WHERE id = %s;", (aluno_id,))
            return cursor.fetchone()


def listar_alunos():
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT id, nome, ra FROM aluno ORDER BY nome, id;")
            return cursor.fetchall()


def buscar_alunos_por_nome(termo):
    termo = (termo or "").strip()
    if not termo:
        return []
    # Trata curingas do LIKE como texto digitado, mantendo a busca por substring.
    termo = termo.replace("!", "!!").replace("%", "!%").replace("_", "!_")
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT id, nome, ra
                FROM aluno
                WHERE nome ILIKE %s ESCAPE '!'
                ORDER BY nome, id;
            """, (f"%{termo}%",))
            return cursor.fetchall()


def normalizar_semestre_ano_ingresso(valor):
    valor = (valor or "").strip()
    if valor and re.fullmatch(r"[12]/[0-9]{4}", valor) is None:
        raise ValueError(
            "Informe o Semestre/Ano de ingresso no formato 1/2027 ou 2/2027 "
            "(semestre 1 ou 2 e ano com quatro dígitos)."
        )
    return valor


def criar_analise(aluno_id, semestre_ano=""):
    semestre_ano = normalizar_semestre_ano_ingresso(semestre_ano)
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO analise (
                    aluno_id,
                    semestre_ano
                )
                VALUES (%s, %s)
                RETURNING id;
            """, (
                aluno_id,
                semestre_ano
            ))

            return cursor.fetchone()[0]


# Mantém os índices usados pelas páginas anteriores e acrescenta dados de origem.
_SELECT_ANALISE = """
    SELECT a.id, al.nome, al.ra, a.semestre_ano, a.situacao_origem,
           a.procedencia, a.data_criacao, a.curso_id, a.matriz_id, a.aluno_id,
           a.curso_origem
    FROM analise a
    JOIN aluno al ON al.id = a.aluno_id
"""


def listar_analises():
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(_SELECT_ANALISE + " ORDER BY a.data_criacao DESC, a.id DESC;")

            return cursor.fetchall()


def obter_analise(analise_id):
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(_SELECT_ANALISE + " WHERE a.id = %s;", (analise_id,))

            return cursor.fetchone()


def atualizar_analise(analise_id, semestre_ano):
    semestre_ano = normalizar_semestre_ano_ingresso(semestre_ano)
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                UPDATE analise
                SET semestre_ano = %s
                WHERE id = %s;
            """, (
                semestre_ano,
                analise_id
            ))


def salvar_origem_aproveitamento(
    analise_id,
    curso_origem,
    situacao_origem,
    procedencia
):
    curso_origem = (curso_origem or "").strip() or None
    situacao_origem = (situacao_origem or "").strip() or None
    procedencia = (procedencia or "").strip() or None
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                UPDATE analise
                SET curso_origem = %s,
                    situacao_origem = %s,
                    procedencia = %s
                WHERE id = %s;
            """, (
                curso_origem,
                situacao_origem,
                procedencia,
                analise_id
            ))


def salvar_curso_e_matriz(analise_id, curso_id, matriz_id):
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                UPDATE analise
                SET
                    curso_id = %s,
                    matriz_id = %s
                WHERE id = %s;
            """, (
                curso_id,
                matriz_id,
                analise_id
            ))
