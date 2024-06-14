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
        return jsonify({'error': 'Error al conectar'}), 500

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
            return jsonify({'error': 'La dirección de correo electrónico ya está en uso. Por favor, elija o introduzca otra.'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'Faltan datos requeridos'}), 400

# Endpoint para obtener todos los usuarios
@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    conn = connect_to_database()
    if not conn:
        return jsonify({'error': 'Error al conectar'}), 500

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
        return jsonify({'error': 'Error al obtener usuarios existentes'}), 500
    finally:
        conn.close()

# Endpoint para validar un usuario
@app.route('/api/usuarios/login', methods=['POST'])
def login_usuario():
    conn = connect_to_database()
    if not conn:
        return jsonify({'error': 'Error al conectar'}), 500

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
            return jsonify({'error': 'Error al validar usuario'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'Faltan datos requeridos'}), 400
    

# Endpoint para crear un nuevo libro
@app.route('/api/libros', methods=['POST'])
def crear_libro():
    conn = connect_to_database()
    if not conn:
        return jsonify({'error': 'Error al conectar'}), 500

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    editorial = data.get('editorial')
    fecha_publicacion = data.get('fecha_publicacion')
    isbn = data.get('isbn')
    numero_paginas = data.get('numero_paginas')
    genero = data.get('genero')
    idioma = data.get('idioma')

    if titulo and autor and editorial and fecha_publicacion and isbn and numero_paginas and genero and idioma:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO libros (titulo, autor, editorial, fecha_publicacion, isbn, numero_paginas, genero, idioma)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (titulo, autor, editorial, fecha_publicacion, isbn, numero_paginas, genero, idioma))
            conn.commit()
            cursor.close()
            return jsonify({'mensaje': 'Libro creado exitosamente'}), 201
        except psycopg2.Error as e:
            return jsonify({'error': 'Error al insertar'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'Faltan datos requeridos'}), 400


# Endpoint para obtener libros paginados
@app.route('/api/libros', methods=['GET'])
def obtener_libros():
    conn = connect_to_database()
    if not conn:
        return jsonify({'error': 'Error al conectar'}), 500

    # Obtén los parámetros de paginación de la solicitud
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, titulo, autor, editorial, fecha_publicacion, isbn, numero_paginas, genero, idioma, fecha_creacion
            FROM libros
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        libros = cursor.fetchall()

        libros_json = []
        for libro in libros:
            libro_dict = {
                'id': libro[0],
                'titulo': libro[1],
                'autor': libro[2],
                'editorial': libro[3],
                'fecha_publicacion': libro[4].strftime("%Y-%m-%d"),
                'isbn': libro[5],
                'numero_paginas': libro[6],
                'genero': libro[7],
                'idioma': libro[8],
                'fecha_creacion': libro[9].strftime("%Y-%m-%d %H:%M:%S")
            }
            libros_json.append(libro_dict)

        cursor.close()
        return jsonify(libros_json), 200
    except psycopg2.Error as e:
        return jsonify({'error': 'Error al obtener libros existentes'}), 500
    finally:
        conn.close()


# Endpoint para agregar un libro a la biblioteca personal del usuario
@app.route('/api/biblioteca_personal', methods=['POST'])
def agregar_libro_a_biblioteca_personal():
    conn = connect_to_database()
    if not conn:
        return jsonify({'error': 'Error al conectar'}), 500

    data = request.get_json()
    usuario_id = data.get('usuario_id')
    libro_id = data.get('libro_id')

    if usuario_id and libro_id:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM biblioteca_personal WHERE usuario_id = %s AND libro_id = %s
            """, (usuario_id, libro_id))
            exists = cursor.fetchone()

            if exists:
                return jsonify({'mensaje': 'El libro ya se añadió anteriormente'}), 409

            cursor.execute("""
                INSERT INTO biblioteca_personal (usuario_id, libro_id)
                VALUES (%s, %s)
            """, (usuario_id, libro_id))
            conn.commit()
            cursor.close()
            return jsonify({'mensaje': 'Libro agregado a la biblioteca personal'}), 201
        except psycopg2.Error as e:
            return jsonify({'error': 'Error al agregar libro a la biblioteca personal'}), 500
        finally:
            conn.close

if __name__ == '__main__':
    app.run(debug=True)
# comentario