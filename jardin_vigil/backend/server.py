from flask import Flask, jsonify, request, send_from_directory
from flask_jwt_extended import create_access_token, JWTManager, jwt_required
from flask_cors import cross_origin, CORS
from flask_mail import Mail, Message
from conexion import conexion, cerrar_conexion
from datetime import timedelta
from dotenv import load_dotenv
import os
import bcrypt
import mysql.connector
from werkzeug.utils import secure_filename


load_dotenv('config.env')
app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)
app.config['UPLOAD_FOLDER'] = 'img_noticias'
app.config['UPLOAD_FOLDER_SALITAS'] = 'img_salitas'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)



@app.route('/verificarSesion', methods=['GET'])
@cross_origin()
@jwt_required()
def verificarSesion():
    return jsonify({"isLoggedIn": True, "role": "admin"}), 200

@app.route('/nuevoUsuario', methods=['POST'])
@cross_origin()
@jwt_required()
def nuevoUsuario():
    datos = request.get_json()
    nombre = datos['nombre']
    apellido = datos['apellido']
    email = datos['email']
    password = datos['password']
    cargo = datos['cargo']
    id_salita = datos['salita'] if datos['cargo'] != '1' and datos['cargo'].lower() != 'director' else None
    estado = 1
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor()
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        nombre_salita = None
        if id_salita:
            cursor.execute("SELECT nombre_salita FROM salitas WHERE id_salita = %s", (id_salita,))
            resultado = cursor.fetchone()
            if resultado:
                nombre_salita = resultado[0]

        query = "INSERT INTO usuarios (nombre, apellido, email, password, cargo, salita_a_cargo, fecha_registro, estado) VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)"
        cursor.execute(query, (nombre, apellido, email, hashed_password, cargo, id_salita, estado))
        db_conexion.commit()
        if cursor.rowcount:
            # Enviar email de confirmación
            mensaje = Message('Registro Exitoso', recipients=[email])
            mensaje.body = f"Hola {nombre} {apellido},\n\nBienvenido/a a parte del equipo de Jardin Constancio C. Vigil 901\n\nYa puedes acceder a tu cuenta en la siguiente URL: http://localhost/proyecto_jardin/jardin_vigil/"
            if nombre_salita:
                mensaje.body += f"\n\nTe han asignado a la salita: {nombre_salita}. ¡Esperamos que disfrutes mucho trabajando con los pequeños!"
            mail.send(mensaje)
            return jsonify({"mensaje": "Usuario registrado exitosamente"}), 200
        else:
            return jsonify({"mensaje": "Error al registrar usuario"}), 500
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    datos = request.get_json()
    email = datos['email']
    password = datos['password'].encode('utf-8')
    db_conexion = None
    cursor = None

    try:
        db_conexion = conexion()
        if not db_conexion:
            print("Fallo al conectar con la base de datos.")
            return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

        cursor = db_conexion.cursor()
        query = "SELECT password, id_usuario, estado, cargo, nombre, apellido, salita_a_cargo FROM usuarios WHERE email = %s"
        cursor.execute(query, (email,))
        resultado = cursor.fetchone()

        if resultado:
            db_password, id_usuario, estado, cargo, nombre, apellido, salita_a_cargo = resultado
            if estado == 1:
                if bcrypt.checkpw(password, db_password.encode('utf-8')):
                    token = create_access_token(identity={"id_usuario": id_usuario, "email": email, "cargo": cargo}, expires_delta=timedelta(days=365))
                    return jsonify({"mensaje": "Login exitoso", "id_usuario": id_usuario, "token": token, "cargo": cargo, "nombre": nombre, "apellido": apellido, "salita_a_cargo": salita_a_cargo}), 200
                else:
                    return jsonify({"mensaje": "Usuario o contraseña incorrecta"}), 401
            else:
                print("Cuenta deshabilitada.")
                return jsonify({"mensaje": "Cuenta deshabilitada"}), 401
        else:
            return jsonify({"mensaje": "Usuario o contraseña incorrecta"}), 401
    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        if cursor:
            try:
                cursor.fetchall()
            except mysql.connector.errors.InterfaceError:
                pass
            cursor.close()
        if db_conexion:
            db_conexion.close()

@app.route('/nuevanoticia', methods=['POST'])
@cross_origin()
@jwt_required()
def nuevanoticia():
    if 'multipart/form-data' not in request.content_type:
        return jsonify({"mensaje": "Tipo de contenido no soportado"}), 415
    titulo = request.form['titulo']
    contenido = request.form['contenido']
    fk_usuario = request.form['fk_usuario']
    resumen = request.form['resumen']
    image_url = None  

    if 'imagen' in request.files:
        imagen = request.files['imagen']
        filename = secure_filename(imagen.filename)
        ruta_imagen = os.path.join('img_noticias', filename)
        
        if os.path.exists(ruta_imagen):
            base, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(ruta_imagen):
                filename = f"{base}_{counter}{extension}"
                ruta_imagen = os.path.join('img_noticias', filename)
                counter += 1
        
        imagen.save(ruta_imagen)
        image_url = ruta_imagen  

    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor()
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        query = "INSERT INTO noticias (titulo, contenido, fk_usuario, fecha_publicacion, image_url, resumen, estado) VALUES (%s, %s, %s, NOW(), %s, %s, %s)"
        cursor.execute(query, (titulo, contenido, fk_usuario, image_url, resumen, 1 ))
        db_conexion.commit()
        if cursor.rowcount:
            return jsonify({"mensaje": "Noticia registrada exitosamente"}), 200
        else:
            return jsonify({"mensaje": "Error al registrar la noticia"}), 500
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/img_noticias/<path:filename>')
def serve_image(filename):
    return send_from_directory('img_noticias', filename)


@app.route('/obtener_noticias', methods=['GET'])
@cross_origin()
def obtener_noticias():
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor()
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        query = "SELECT id_noticia, titulo, contenido, fk_usuario, fecha_publicacion, image_url, resumen, estado FROM noticias WHERE estado = 1 ORDER BY fecha_publicacion DESC"
        cursor.execute(query)
        noticias = cursor.fetchall()
        noticias_lista = [
            {"id_noticia": noticia[0], "titulo": noticia[1], "contenido": noticia[2], "fk_usuario": noticia[3], 
             "fecha_publicacion": noticia[4].strftime('%d/%m/%Y'), 
             "image_url": f"http://127.0.0.1:5000/img_noticias/{os.path.basename(noticia[5]) if noticia[5] else 'default.png'}",
             "resumen": noticia[6], "estado": noticia[7]}
            for noticia in noticias
        ]
        return jsonify(noticias_lista), 200
    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/modificarnoticia', methods=['POST'])
@cross_origin()
@jwt_required()
def modificar_noticia():
    if 'multipart/form-data' not in request.content_type:
        return jsonify({"mensaje": "Tipo de contenido no soportado"}), 415

    id_noticia = request.form['id_noticia']
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("SELECT * FROM noticias WHERE id_noticia = %s", (id_noticia,))
        noticia_actual = cursor.fetchone()
        if noticia_actual is None:
            return jsonify({"mensaje": "Noticia no encontrada"}), 404
        
        campos = ["titulo", "contenido", "fk_usuario", "fecha_publicacion", "image_url", "resumen", "estado"]
        cambios = {}
        for campo in campos:
            valor_actual = noticia_actual.get(campo)
            valor_nuevo = request.form.get(campo)
            if valor_nuevo and valor_nuevo != valor_actual:
                cambios[campo] = valor_nuevo

        image_url = noticia_actual['image_url']
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            ruta_imagen = os.path.join('img_noticias', secure_filename(imagen.filename))
            imagen.save(ruta_imagen)
            image_url = f"http://127.0.0.1:5000/img_noticias/{secure_filename(os.path.basename(ruta_imagen))}"
            cambios['image_url'] = image_url

        if cambios:
            sets = ", ".join([f"{campo} = %s" for campo in cambios])
            valores = list(cambios.values())
            valores.append(id_noticia)
            cursor.execute(f"UPDATE noticias SET {sets} WHERE id_noticia = %s", valores)
            db_conexion.commit()
            return jsonify({"mensaje": "Noticia actualizada exitosamente"}), 200
        else:
            return jsonify({"mensaje": "No se detectaron cambios para actualizar"}), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/modificarusuario', methods=['POST'])
@cross_origin()
@jwt_required()
def modificar_usuario():
    datos_nuevos = request.json
    id_usuario = datos_nuevos.get('id_usuario')
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        usuario_actual = cursor.fetchone()
        if usuario_actual is None:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
        
        campos = ["nombre", "apellido", "email", "cargo", "salita_a_cargo", "estado"]
        cambios = {}
        for campo in campos:
            valor_actual = usuario_actual.get(campo)
            valor_nuevo = datos_nuevos.get(campo)
            if valor_nuevo is not None and valor_nuevo != valor_actual:
                cambios[campo] = valor_nuevo
        
        # Verificar si se proporciona una nueva contraseña
        if 'password' in datos_nuevos:
            password_nueva = datos_nuevos['password']
            if password_nueva:
                hashed_password = bcrypt.hashpw(password_nueva.encode('utf-8'), bcrypt.gensalt())
                cambios['password'] = hashed_password
        
        if cambios:
            sets = ", ".join([f"{campo} = %s" for campo in cambios])
            valores = list(cambios.values())
            valores.append(id_usuario)
            cursor.execute(f"UPDATE usuarios SET {sets} WHERE id_usuario = %s", valores)
            db_conexion.commit()
            return jsonify({"mensaje": "Usuario actualizado exitosamente"}), 200
        else:
            return jsonify({"mensaje": "No se detectaron cambios para actualizar"}), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/eliminarusuario', methods=['DELETE'])
@cross_origin()
def eliminar_usuario():
    db_conexion = conexion()
    datos = request.json
    id_usuario = datos.get('id_usuario')
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor()
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        query = "DELETE FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        db_conexion.commit()
        if cursor.rowcount:
            return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el usuario"}), 500
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)


@app.route('/traercargos', methods=['POST'])
@cross_origin()
def traer_cargos():
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    try:
        with db_conexion.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id_cargo, nombre_cargo FROM cargos")
            cargos = cursor.fetchall()
            if not cargos:
                return jsonify({"mensaje": "No se encontraron cargos"}), 404
            cargos_dict = [{"id_cargo": cargo['id_cargo'], "nombre_cargo": cargo['nombre_cargo']} for cargo in cargos]
            return jsonify({"cargos": cargos_dict}), 200
    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/img_salitas/<path:filename>')
def serve_image_salitas(filename):
    return send_from_directory('img_salitas', filename)


@app.route('/traersalitas', methods=['POST'])
@cross_origin()
def traer_salitas():
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("""
            SELECT s.id_salita, s.nombre_salita, t.nombre_turno AS turno_salita, s.informacion_salita, 
                   s.body_bg_color_salita, s.header_bg_color_salita, s.color_texto_principal_salita, s.url_img_principal, s.estado 
            FROM salitas s 
            INNER JOIN turnos t ON s.turno_salita = t.id_turno
        """)
        salitas = cursor.fetchall()
        salitas_procesadas = [
            {
                "id_salita": salita['id_salita'], 
                "nombre_salita": salita['nombre_salita'], 
                "turno_salita": salita['turno_salita'], 
                "informacion_salita": salita['informacion_salita'],
                "body_bg_color_salita": salita['body_bg_color_salita'],
                "color_texto_principal_salita": salita['color_texto_principal_salita'],
                "header_bg_color_salita": salita['header_bg_color_salita'],
                "url_img_principal": f"http://127.0.0.1:5000/img_salitas/{os.path.basename(salita['url_img_principal']) if salita['url_img_principal'] else 'default.png'}",
                "estado": "Activa" if salita['estado'] == 1 else "Inactiva"
            } 
            for salita in salitas
        ]
        if salitas_procesadas:
            return jsonify({"salitas": salitas_procesadas}), 200
        else:
            return jsonify({"mensaje": "No hay salitas registradas"}), 404
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/nuevasalita', methods=['POST'])
@cross_origin()
@jwt_required()
def nueva_salita():
    datos = request.get_json()
    nombre_salita = datos['nombre_salita']
    turno_salita = datos['turno_salita']
    if turno_salita == "0":
        return jsonify({"mensaje": "Por favor, seleccione un turno válido."}), 400
    estado = 1
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("INSERT INTO salitas (nombre_salita, turno_salita, estado) VALUES (%s, %s, %s)", (nombre_salita, turno_salita, estado))
        db_conexion.commit()
        return jsonify({"mensaje": "Salita ingresada exitosamente"}), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/modificarsalita', methods=['POST'])
@cross_origin()
@jwt_required()
def modificar_salita():
    datos = request.form.to_dict()
    id_salita = datos['id_salita']
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("SELECT * FROM salitas WHERE id_salita = %s", (id_salita,))
        salita_actual = cursor.fetchone()
        if salita_actual is None:
            return jsonify({"mensaje": "Salita no encontrada"}), 404
        
        campos = ["nombre_salita", "turno_salita", "estado", "url_img_principal" , "body_bg_color_salita","header_bg_color_salita", "color_texto_principal_salita"]
        cambios = {}
        for campo in campos:
            valor_actual = salita_actual.get(campo)
            valor_nuevo = datos.get(campo)
            if valor_nuevo and valor_nuevo != valor_actual:
                cambios[campo] = valor_nuevo

        # Manejo de la imagen principal
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen.filename != '':
                # Obtener la imagen actual de la base de datos
                cursor.execute("SELECT url_img_principal FROM salitas WHERE id_salita = %s", (id_salita,))
                imagen_actual = cursor.fetchone()['url_img_principal']
                
                # Generar un nombre de archivo único
                filename = secure_filename(f"{id_salita}_{imagen.filename}")
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER_SALITAS'], filename))
                url_img_principal = f"http://127.0.0.1:5000/{app.config['UPLOAD_FOLDER_SALITAS']}/{filename}"
                cambios['url_img_principal'] = url_img_principal

        if cambios:
            sets = ", ".join([f"{campo} = %s" for campo in cambios])
            valores = list(cambios.values())
            valores.append(id_salita)
            cursor.execute(f"UPDATE salitas SET {sets} WHERE id_salita = %s", valores)
            db_conexion.commit()
            return jsonify({"mensaje": "Salita actualizada exitosamente"}), 200
        else:
            return jsonify({"mensaje": "No se detectaron cambios para actualizar"}), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/eliminarsalita', methods=['DELETE'])
@cross_origin()
def eliminar_salita():
    db_conexion = conexion()
    datos = request.json
    id_salita = datos.get('id_salita')
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor()
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        query = "DELETE FROM salitas WHERE id_salita = %s"
        cursor.execute(query, (id_salita,))
        db_conexion.commit()
        if cursor.rowcount:
            return jsonify({"mensaje": "Salita eliminada exitosamente"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar la salita"}), 500
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)        

@app.route('/nuevocargo', methods=['POST'])
@cross_origin()
@jwt_required()
def nuevo_cargo():
    datos = request.get_json()
    nombre_cargo = datos['nombre_cargo']
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("INSERT INTO cargos (nombre_cargo) VALUES (%s)", (nombre_cargo,))
        db_conexion.commit()
        return jsonify({"mensaje": "Cargo creado exitosamente"}), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/traerturnos', methods=['GET'])
@cross_origin()
def traer_turnos():
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("SELECT id_turno, nombre_turno FROM turnos")
        turnos = cursor.fetchall()
        turnos_diferenciados = [{"id_turno": turno['id_turno'], "nombre_turno": turno['nombre_turno']} for turno in turnos]
        return jsonify(turnos_diferenciados), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)
        print("Conexión Cerrada")


@app.route('/obtener_usuarios', methods=['GET'])
@cross_origin()
@jwt_required()
def obtener_usuarios():
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("""
            SELECT 
                u.id_usuario, 
                u.nombre, 
                u.apellido, 
                u.email, 
                c.nombre_cargo AS cargo, 
                s.nombre_salita AS salita_a_cargo 
            FROM 
                usuarios u
                LEFT JOIN cargos c ON u.cargo = c.id_cargo
                LEFT JOIN salitas s ON u.salita_a_cargo = s.id_salita
        """)
        usuarios = cursor.fetchall()
        usuarios_diferenciados = [
            {
                "id_usuario": usuario['id_usuario'], 
                "nombre": usuario['nombre'], 
                "apellido": usuario['apellido'], 
                "email": usuario['email'], 
                "cargo": usuario['cargo'], 
                "salita_a_cargo": usuario['salita_a_cargo']
            } 
            for usuario in usuarios
        ]
        return jsonify(usuarios_diferenciados), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)
        print("Conexión Cerrada")


@app.route('/nuevoHorario', methods=['POST'])
@cross_origin()
@jwt_required()
def nuevo_horario():
    datos = request.get_json()
    id_salita = datos['id_salita']
    dias_semana = datos['dia_semana']  
    hora_inicio = datos['hora_inicio']
    hora_fin = datos['hora_fin']
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        for dia in dias_semana:  
            cursor.execute("INSERT INTO horarios (fk_salita, dia_semana, hora_inicio, hora_fin, fecha_creacion) VALUES (%s, %s, %s, %s, NOW())", (id_salita, dia, hora_inicio, hora_fin))
        db_conexion.commit()
        return jsonify({"mensaje": "Horario ingresado exitosamente"}), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/traerHorarios', methods=['GET'])
@cross_origin()
def traer_horarios():
    id_salita = request.args.get('id_salita')
    if not id_salita:
        return jsonify({"mensaje": "No se proporcionó el ID de la salita"}), 400

    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500

    try:
        with db_conexion.cursor(dictionary=True) as cursor:
            consulta = """
            SELECT h.id_horario, h.fk_salita, ds.nombre_dia as dia_semana, h.hora_inicio, h.hora_fin
            FROM horarios h
            INNER JOIN dias_semana ds ON h.dia_semana = ds.id_dia
            WHERE h.fk_salita = %s
            """
            cursor.execute(consulta, (id_salita,))
            horarios = cursor.fetchall()
            if not horarios:
                return jsonify({"mensaje": "No se encontraron horarios para la salita especificada"}), 404

            horarios_formateados = [{
                "id_horario": horario['id_horario'],
                "dia_semana": horario['dia_semana'],
                "hora_inicio": str(horario['hora_inicio']),
                "hora_fin": str(horario['hora_fin'])
            } for horario in horarios]

            return jsonify({"horarios": horarios_formateados}), 200
    except Exception as e:
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)

@app.route('/modificarhorario', methods=['POST'])
@cross_origin()
@jwt_required()
def modificar_horario():
    datos = request.json
    id_horario = datos.get('id_horario')
    db_conexion = conexion()
    if not db_conexion:
        print("Fallo al conectar con la base de datos.")
        return jsonify({"mensaje": "Error de conexión a la base de datos"}), 500
    cursor = db_conexion.cursor(dictionary=True)
    if not cursor:
        cerrar_conexion(db_conexion)
        print("Fallo al crear el cursor.")
        return jsonify({"mensaje": "Error al crear el cursor"}), 500
    try:
        cursor.execute("SELECT * FROM horarios WHERE id_horario = %s", (id_horario,))
        horario_actual = cursor.fetchone()
        if horario_actual is None:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404
        
        campos = ["hora_inicio", "hora_fin"]
        cambios = {}
        for campo in campos:
            valor_actual = horario_actual.get(campo)
            valor_nuevo = datos.get(campo)
            if valor_nuevo is not None and valor_nuevo != valor_actual:
                cambios[campo] = valor_nuevo
        
        if cambios:
            sets = ", ".join([f"{campo} = %s" for campo in cambios])
            valores = list(cambios.values())
            valores.append(id_horario)
            cursor.execute(f"UPDATE horarios SET {sets} WHERE id_horario = %s", valores)
            db_conexion.commit()
            return jsonify({"mensaje": "Horario actualizado exitosamente"}), 200
        else:
            return jsonify({"mensaje": "No se detectaron cambios para actualizar"}), 200
    except Exception as e:
        db_conexion.rollback()
        print(f"Error al ejecutar la consulta: {str(e)}")
        return jsonify({"mensaje": "Error al ejecutar la consulta", "error": str(e)}), 500
    finally:
        cerrar_conexion(db_conexion)


if __name__ == '__main__':
    app.run(debug=True)