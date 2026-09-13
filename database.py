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