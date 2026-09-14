import os

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

def criar_analise(nome_aluno, ra, semestre_ano, situacao, procedencia):
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO analise (
                    nome_aluno,
                    ra,
                    semestre_ano,
                    situacao,
                    procedencia
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                nome_aluno,
                ra,
                semestre_ano,
                situacao,
                procedencia
            ))

            return cursor.fetchone()[0]


def listar_analises():
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    nome_aluno,
                    ra,
                    semestre_ano,
                    situacao,
                    procedencia,
                    data_criacao
                FROM analise
                ORDER BY data_criacao DESC;
            """)

            return cursor.fetchall()


def obter_analise(analise_id):
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    nome_aluno,
                    ra,
                    semestre_ano,
                    situacao,
                    procedencia,
                    data_criacao,
                    curso_id,
                    matriz_id
                FROM analise
                WHERE id = %s;
            """, (analise_id,))

            return cursor.fetchone()


def atualizar_analise(
    analise_id,
    nome_aluno,
    ra,
    semestre_ano,
    situacao,
    procedencia
):
    with obter_conexao() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                UPDATE analise
                SET
                    nome_aluno = %s,
                    ra = %s,
                    semestre_ano = %s,
                    situacao = %s,
                    procedencia = %s
                WHERE id = %s;
            """, (
                nome_aluno,
                ra,
                semestre_ano,
                situacao,
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