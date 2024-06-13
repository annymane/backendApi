# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from bdd.connection import connect_to_database  # Importa la función de conexión desde connection.py
import psycopg2

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Ejemplo de ruta para probar la conexión
@app.route('/')
def index():
    conn = connect_to_database()  # Llama a la función para establecer la conexión
    if conn:
        return 'Conexión exitosa a PostgreSQL'
    else:
        return 'Error al conectar a PostgreSQL'

# Endpoint para crear un nuevo usuario
@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    conn = connect_to_database()
    if not conn:
        return jsonify({'error': 'Error al conectar a PostgreSQL'}), 500

    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')
    contraseña = data.get('contraseña')

    if nombre and email and contraseña:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, contraseña)
                VALUES (%s, %s, %s)
            """, (nombre, email, contraseña))
            conn.commit()
            cursor.close()
            return jsonify({'mensaje': 'Usuario creado exitosamente'}), 201
        except psycopg2.Error as e:
            print("Error al insertar usuario en PostgreSQL:", e)
            return jsonify({'error': 'Error al insertar usuario en PostgreSQL'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'Faltan datos requeridos'}), 400

# Endpoint para obtener todos los usuarios
@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    conn = connect_to_database()
    if not conn:
        return jsonify({'error': 'Error al conectar a PostgreSQL'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, email, fecha_creacion FROM usuarios")
        usuarios = cursor.fetchall()

        usuarios_json = []
        for usuario in usuarios:
            usuario_dict = {
                'id': usuario[0],
                'nombre': usuario[1],
                'email': usuario[2],
                'fecha_creacion': usuario[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            usuarios_json.append(usuario_dict)

        cursor.close()
        return jsonify(usuarios_json), 200
    except psycopg2.Error as e:
        print("Error al obtener usuarios de PostgreSQL:", e)
        return jsonify({'error': 'Error al obtener usuarios de PostgreSQL'}), 500
    finally:
        conn.close()

# Endpoint para validar un usuario
@app.route('/api/usuarios/login', methods=['POST'])
def login_usuario():
    conn = connect_to_database()
    if not conn:
        return jsonify({'error': 'Error al conectar a PostgreSQL'}), 500

    data = request.get_json()
    email = data.get('email')
    contraseña = data.get('contraseña')

    if email and contraseña:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, email
                FROM usuarios
                WHERE email = %s AND contraseña = %s
            """, (email, contraseña))
            usuario = cursor.fetchone()
            cursor.close()

            if usuario:
                usuario_dict = {
                    'id': usuario[0],
                    'nombre': usuario[1],
                    'email': usuario[2]
                }
                return jsonify({'mensaje': 'Login exitoso', 'usuario': usuario_dict}), 200
            else:
                return jsonify({'mensaje': 'Credenciales incorrectas'}), 401
        except psycopg2.Error as e:
            print("Error al validar usuario en PostgreSQL:", e)
            return jsonify({'error': 'Error al validar usuario en PostgreSQL'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'Faltan datos requeridos'}), 400

if __name__ == '__main__':
    app.run(debug=True)
