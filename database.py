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