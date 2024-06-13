# connection.py

import psycopg2

def connect_to_database():
    try:
        conn = psycopg2.connect(
            user="postgres",
            password="pamejuly",
            host="localhost",
            database="bibliotecavirtual"
        )
        print("Conexión a PostgreSQL exitosa")
        return conn
    except psycopg2.Error as e:
        print("Error al conectar a PostgreSQL:", e)
        return None
