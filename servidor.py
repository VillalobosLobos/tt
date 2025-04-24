from flask import Flask, json, request,render_template,jsonify, session,redirect, url_for, flash
from mysql.connector import Error, OperationalError
from mysql.connector.errors import IntegrityError
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from email.mime.text import MIMEText
from flask_session import Session
from mysql.connector import Error
from flask import jsonify
import mysql.connector
import numpy as np
import secrets
import smtplib
import hashlib
import random
import string
import os

coneccion=mysql.connector.connect(
	host="localhost",
	user="villalobos",
	password="root",
	database="tt"
)

cursor=coneccion.cursor()

app = Flask(__name__)

#Configuración de la sesión
app.secret_key = 'tt'
tokens_recuperacion = {}
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = './flask_session'
Session(app)

app.config['UPLOAD_FOLDER'] = 'static/img/usuarios'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

tokens_recuperacion = {}
token=""
correoAux=""

def generar_codigo_unico():
    while True:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))  # Ej: "A1B2C"
        cursor = coneccion.cursor()
        cursor.execute("SELECT Codigo FROM Grupo WHERE Codigo = %s;", (codigo,))
        resultado = cursor.fetchone()
        cursor.close()

        if not resultado:  # Si el código no está en la BD, es único y lo usamos
            return codigo

def generar_codigo():
    caracteres = string.ascii_uppercase + string.digits
    codigo = ''.join(random.choices(caracteres, k=5))
    return codigo

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/acabarActividadesP')
def acabarActividadesP():
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))
    
    correo_alumno = session['usuario']['CorreoTutor']
    bien = request.args.get('bien', default=0, type=int)
    mal = request.args.get('mal', default=0, type=int)

    cursor = coneccion.cursor()
    cursor.execute("SELECT IdAlumno FROM Alumno WHERE CorreoTutor = %s", (correo_alumno,))
    alumno = cursor.fetchone()

    if alumno:
        id_alumno = alumno[0]
        id_ejercicio = session.get('id_ejercicio')
        if id_ejercicio:
            cursor.execute("""
                INSERT INTO Resultado (IdAlumno, IdEjercicio, Aciertos, Errores)
                VALUES (%s, %s, %s, %s)
            """, (id_alumno, id_ejercicio, bien, mal))
            coneccion.commit()
        else:
            print("⚠️ No se encontró id_ejercicio en la sesión")
    else:
        print("⚠️ No se encontró alumno con ese correo")

    return render_template('pages/concluirP.html', bien=bien, mal=mal)

@app.route('/ejercicio')
def ejercicio():
    id = request.args.get('id')
    if not id:
        return "ID de ejercicio no proporcionado", 400

    # Guardar el id del ejercicio en la sesión para usarlo más tarde
    session['id_ejercicio'] = int(id)

    # Obtener los valores del ejercicio
    cursor.execute("SELECT Valores FROM Ejercicio WHERE IdEjercicio = %s;", (id,))
    resultado = cursor.fetchone()

    if not resultado:
        return "Ejercicio no encontrado", 404

    valores = json.loads(resultado[0].decode('utf-8'))

    return render_template('pages/ejercicio.html', ejercicio=valores)

@app.route('/ejerciciosAlumnos')
def ejerciciosAlumnos():
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))

    correo_tutor = session['usuario'].get('CorreoTutor')

    cursor = coneccion.cursor(dictionary=True)

    cursor.execute("SELECT IdAlumno, Nombre, Apellido, Foto, CorreoTutor, IdGrupo FROM Alumno WHERE CorreoTutor = %s;", (correo_tutor,))
    alumno_info = cursor.fetchone()

    id_grupo = alumno_info.get('IdGrupo')

    cursor.execute("SELECT CorreoDocente FROM Grupo WHERE IdGrupo = %s;", (id_grupo,))
    grupo_info = cursor.fetchone()

    correo_docente = grupo_info.get('CorreoDocente')
    cursor.close()

    cursor = coneccion.cursor()
    cursor.execute("SELECT Titulo,IdEjercicio FROM Ejercicio WHERE CorreoDocente=%s;",(correo_docente,))
    ejerciciosTitulos = cursor.fetchall()

    return render_template('/pages/ejerciciosAlumnos.html',ejercicios=ejerciciosTitulos)

@app.route('/actualizar-ejercicio', methods=['PUT'])
def actualizar_ejercicio():
    data = request.get_json()
    ejercicio_id = data.get('id')
    nuevo_titulo = data.get('titulo')
    nuevos_valores = data.get('valores')

    valores_json = json.dumps(nuevos_valores)

    cursor = coneccion.cursor()
    cursor.execute(
        "UPDATE Ejercicio SET Titulo=%s, Valores=%s WHERE IdEjercicio=%s;",
        (nuevo_titulo, valores_json, ejercicio_id)
    )
    coneccion.commit()
    cursor.close()  # Buen hábito cerrar el cursor

    return jsonify({'mensaje': 'Ejercicio actualizado correctamente'})

@app.route("/actualizarEjercicioPagina")
def actualizarEjercicio():
    id=request.args.get('id')
    
    cursor = coneccion.cursor()
    cursor.execute("SELECT * FROM Ejercicio WHERE IdEjercicio=%s;",(id,))
    ejercicio = cursor.fetchone()
    respuesta=json.loads(ejercicio[2].decode('utf-8'))

    return render_template('/pages/actualizarEjercicio.html',ejercicio=ejercicio,respuesta=respuesta)

@app.route("/eliminarEjercicio")
def eliminarEjercicio():
    id=request.args.get('id')
    
    cursor = coneccion.cursor()
    cursor.execute("delete from Ejercicio where IdEjercicio=%s;", (id,))
    coneccion.commit()
    
    return redirect(request.referrer or '/')

@app.route('/crud')
def crud():
    correo = request.args.get('correo')  # esto es lo que pasaste en la URL

    cursor = coneccion.cursor()
    cursor.execute("SELECT Titulo,IdEjercicio FROM Ejercicio WHERE CorreoDocente=%s;",(correo,))
    ejerciciosTitulos = cursor.fetchall()
    print(ejerciciosTitulos)

    # Aquí puedes usar ese correo para filtrar ejercicios, etc.
    return render_template('/pages/crud.html', correo_docente=correo,titulos=ejerciciosTitulos)

@app.route('/subir-ejercicio', methods=['POST'])
def subir_ejercicio():
    data = request.get_json()
    titulo = data.get("titulo")
    valores = data.get("valores")
    correo=data.get("correo")

    print("Título del ejercicio:", titulo)
    print("Valores recibidos:", valores)

    cursor = coneccion.cursor()
    cursor.execute("""
        INSERT INTO Ejercicio (Titulo, Valores, CorreoDocente)
        VALUES (%s, %s, %s)
    """, (titulo, json.dumps(valores), correo))
    coneccion.commit()

    return jsonify({"mensaje": "Ejercicio recibido correctamente", "titulo": titulo, "valores": valores})

@app.route('/crudEjercicios')
def crud_ejercicios():
    correo = request.args.get('correo')
    print("Correo recibido para agregar:", correo)

    # Aquí puedes usar ese correo para filtrar ejercicios, etc.
    return render_template('/pages/crudEjercicios.html', correo_docente=correo)

@app.route('/cambiar_foto', methods=['POST'])
def cambiar_foto():
    if 'foto' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['foto']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        # Obtener el correo del tutor desde los datos del formulario
        correo_tutor = request.form.get('CorreoTutor')
        
        if not correo_tutor:
            return jsonify({"error": "Correo del tutor no proporcionado"}), 400
        # Renombrar el archivo con el correo del tutor
        ext = os.path.splitext(file.filename)[1]  # Obtener la extensión del archivo
        filename = f"{correo_tutor}{ext}"
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        cursor = coneccion.cursor()

        # Realiza la consulta de actualización
        cursor.execute(
            "UPDATE Alumno SET Foto=%s WHERE CorreoTutor=%s", 
            (file_path, correo_tutor)
        )
        coneccion.commit()
        return jsonify({"foto": filename})
    return jsonify({"error": "Archivo no permitido"}), 400

@app.route('/perfil')
def perfil():
    alumno = {'Foto': 'static/usuarios/default.jpg'}
    return render_template('pages/confAlumno.html', alumno=alumno)

@app.route('/eliminarDocente', methods=['POST'])
def eliminarDocente():
    correo = request.form['correo']

    try:
        # Verifica si la conexión está activa
        if not coneccion.is_connected():
            print("Conexión perdida. Intentando reconectar...")
            coneccion.reconnect(attempts=3, delay=5)
            if not coneccion.is_connected():
                raise OperationalError("No se pudo reconectar a la base de datos.")

        cursor = coneccion.cursor()

        # Verificar si el docente existe antes de eliminar
        cursor.execute("SELECT * FROM Docente WHERE CorreoDocente = %s", (correo,))
        docente = cursor.fetchone()
        
        if not docente:
            print(f"No se encontró un docente con el correo: {correo}")
            return render_template("pages/admin.html", message="Docente no encontrado.")

        # Eliminar el docente
        cursor.execute("DELETE FROM Docente WHERE CorreoDocente = %s", (correo,))
        coneccion.commit()

        print(f"Docente con correo {correo} eliminado correctamente.")
        return render_template("pages/admin.html", message="Docente eliminado con éxito.")

    except OperationalError as e:
        print(f"Error de conexión: {e}")
        return render_template("pages/admin.html", message="Error al conectar con la base de datos. Intente más tarde.")

    except Exception as e:
        print(f"Error inesperado: {e}")
        return render_template("pages/admin.html", message="Ocurrió un error inesperado.")

@app.route('/actualizarDocente', methods=['POST'])
def actualizarDocente():
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    correo = request.form['correo']

    try:
        # Verifica si la conexión está activa
        if not coneccion.is_connected():
            print("Conexión perdida. Intentando reconectar...")
            coneccion.reconnect(attempts=3, delay=5)  # Reintenta reconectar 3 veces con un retraso de 5 segundos
            if not coneccion.is_connected():
                raise OperationalError("No se pudo reconectar a la base de datos.")

        cursor = coneccion.cursor()

        # Realiza la consulta de actualización
        cursor.execute(
            "UPDATE Docente SET CorreoDocente=%s, Nombre=%s, Apellido=%s WHERE CorreoDocente=%s", 
            (correo, nombre, apellidos, correo)
        )
        coneccion.commit()  # Guarda los cambios en la base de datos

        print("Actualización exitosa.")
        return render_template("pages/admin.html")

    except OperationalError as e:
        # Si la conexión se pierde, muestra un mensaje de error
        print(f"Error de conexión: {e}")
        return render_template("pages/admin.html", message="Error al conectar con la base de datos. Intente más tarde.")

    except mysql.connector.errors.IntegrityError:
        # Si ya existe un docente con el mismo correo, muestra un mensaje
        print("Error de integridad: El docente ya existe.")
        return render_template("pages/admin.html", message="El docente ya existe.")

    except Exception as e:
        # Captura cualquier otro error y muestra el mensaje
        print(f"Error inesperado: {e}")
        return render_template("pages/admin.html", message="Ocurrió un error inesperado.")

@app.route('/buscarDocente', methods=['POST'])
def buscar_docente():
    data = request.get_json()
    correo = data.get('correo')
    cursor = coneccion.cursor(dictionary=True)

    try:
        # Buscar el docente por correo
        cursor.execute("SELECT * FROM Docente WHERE CorreoDocente = %s", (correo,))
        docente = cursor.fetchone()

        if docente:
                # Si el docente existe, devolver los datos
            print(docente)
            return jsonify({
                'success': True,
                'docente': docente
            })
        else:
            # Si el docente no existe
            return jsonify({
                'success': False
            })

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return jsonify({'success': False})

@app.route('/agregarDocente', methods=['POST'])
def agregarDocente():
    nombre=request.form['nombre']
    apellidos=request.form['apellidos']
    correo=request.form['correo']
    contraseña=request.form['contraseña']
    hash=hashlib.sha256(contraseña.encode()).hexdigest()

    try:
        cursor.execute("INSERT INTO Docente(CorreoDocente,Nombre,Apellido,Contraseña) VALUES (%s,%s,%s,%s)", (correo, nombre,apellidos,hash))
        coneccion.commit()
        return render_template("pages/admin.html",message="Docente guardado correctamente")
    except mysql.connector.errors.IntegrityError:
        return render_template("pages/admin.html",message="El docente ya existe")

@app.route('/admin')
def admin():
    return render_template('pages/admin.html')

@app.route('/restablecer')
def restablecer():
     print(f'correo es : {correoAux}')
     return render_template('pages/restablecer.html')

@app.route('/cambiar_contraseña', methods=['POST'])
def cambiar_contraseña():
    nueva=request.form['nueva_contraseña']
    conf=request.form['confirmar_contraseña']

    if nueva == conf:
        cursor.execute("UPDATE Tutor SET Contraseña=%s WHERE CorreoTutor=%s", (nueva, correoAux))
        coneccion.commit()
        flash("Contraseña cambiada exitosamente.", "success")
        return render_template("index.html")
    else:
        flash("No coinciden las contraseñas", "danger")
        return render_template("pages/restablecer.html")

@app.route('/verificar_codigo', methods=['POST'])
def verificar_codigo():
    codigo=request.form['codigo']

    print(f'codigo: {codigo}\ntoken: {token}')
    if codigo==token:
        return render_template("pages/restablecer.html")
    else:
        return render_template("pages/contraseñaRecuperada.html", mensaje_error="Código incorrecto. Inténtalo de nuevo.")

@app.route("/recuperar_contraseña", methods=["POST"])
def recuperar_contraseña():
    correo = request.form.get("email")
    global correoAux
    correoAux=correo
    codigo=generar_codigo()

    global token
    token=codigo
    print(f'recuperar token: {token}')

    #bmds xqfj iskd vrqk 
    servidor=smtplib.SMTP('smtp.gmail.com',587)
    servidor.starttls()
    servidor.login("eduvoz212@gmail.com","bmds xqfj iskd vrqk")

    msj=MIMEText(f'Tu codigo es: {codigo}')

    msj["From"]="eduvoz212@gmail.com"
    msj["To"]=correo
    msj["Subject"]="Recuperar contraseña"

    servidor.sendmail("eduvoz212@gmail.com",correo,msj.as_string())
    servidor.quit()

    return render_template('pages/contraseñaRecuperada.html')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/cerrar_sesion', methods=['POST'])
def cerrar_sesion():
    # Eliminar la sesión
    session.pop('usuario', None)
    
    # Redirigir a la ruta principal (index)
    return redirect(url_for('index'))

@app.route('/sessionInfo')
def sessionInfo():
    return jsonify(session.get('usuario', 'No hay usuario en sesión'))

@app.route('/inicioSesion')
def sesion():
     return render_template('pages/inicioSesion.html')

@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method=="POST":
        nombre=request.form["nombre"]
        correo=request.form["email"]
        numero=request.form["telefono"]
        mensaje=request.form["mensaje"]

        #bmds xqfj iskd vrqk 
        servidor=smtplib.SMTP('smtp.gmail.com',587)
        servidor.starttls()
        servidor.login("eduvoz212@gmail.com","bmds xqfj iskd vrqk")

        msj=MIMEText(f'Correo: {correo}\nNombre: {nombre}\nNumero: {numero}\n\n{mensaje}')

        msj["From"]=correo
        msj["To"]="eduvoz212@gmail.com"
        msj["Subject"]="Contacto"

        servidor.sendmail(correo,"eduvoz212@gmail.com",msj.as_string())
        servidor.quit()

        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/recuperarContraseña')
def recuperarContraseña():
     return render_template('pages/recuperarContraseña.html')

@app.route('/crearAlumno', methods=["GET", "POST"])
def crearAlumno():
    nombre = request.form['nombre']
    apellidos = request.form['apellido']
    correo = request.form['correo']
    contraseña = request.form['contraseña']

    hash = hashlib.sha256(contraseña.encode()).hexdigest()

    try:
        if request.form.get('remember-me'):
            try:
                cursor.execute("INSERT INTO Tutor (CorreoTutor, Contraseña) VALUES (%s, %s)", (correo, hash))
                coneccion.commit()
                print("Inserción en Tutor exitosa.")
                cursor.execute("INSERT INTO Alumno (Nombre, Apellido, Foto, AciertosNumeros, CorreoTutor, AciertosLetras) VALUES (%s, %s, %s, %s, %s, %s)",(nombre, apellidos, "static/img/alumnos/usuario.png", 0, correo, 0))
                coneccion.commit()
                print("Inserción en Alumno exitosa.")

            except Exception as e:
                coneccion.rollback()  # Revierte cambios si hay error
                print(f"Error en la inserción: {e}")


            return render_template('index.html')

    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # Código de error para entrada duplicada
            return "Error: El correo ya está registrado. Intenta con otro."

    except mysql.connector.Error as e:
        return f"Error en la base de datos: {e}"

    finally:
        cursor.close()
        coneccion.close()
        return render_template('index.html')

@app.route('/crearCuenta')
def crearCuenta():
     return render_template('pages/crearCuenta.html')

@app.route('/ejercicioNumeros')
def ejercicioNumeros():
     return render_template('pages/ejercicioNumeros.html')

@app.route('/acabarNumeros')
def acabarNumeros():
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))
    
    correo_alumno = session['usuario']['CorreoTutor']
    
    bien = request.args.get('bien', default=0, type=int)
    mal=10-bien

    cursor.execute("UPDATE Alumno SET AciertosNumeros=%s WHERE CorreoTutor=%s", (bien, correo_alumno))
    coneccion.commit()

    return render_template('pages/concluir.html', bien=bien, mal=mal)

@app.route('/acabarActividades')
def acabarActividades():
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))
    
    correo_alumno = session['usuario']['CorreoTutor']
    
    bien = request.args.get('bien', default=0, type=int)
    mal=10-bien

    cursor.execute("UPDATE Alumno SET AciertosLetras=%s WHERE CorreoTutor=%s", (bien, correo_alumno))
    coneccion.commit()

    return render_template('pages/concluir.html', bien=bien, mal=mal)

@app.route('/ejercicioLetras')
def ejercicioLetras():
     return render_template('pages/ejercicioLetras.html')

@app.route('/progresoAlumno')
def progresoAlumno():
     if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))
     correo_alumno = session['usuario']['CorreoTutor']

     cursor = coneccion.cursor(dictionary=True)
    
    # Obtener la información del alumno
     cursor.execute("SELECT IdAlumno, Nombre, Apellido, Foto, AciertosNumeros,AciertosLetras, IdGrupo, CorreoTutor FROM Alumno WHERE CorreoTutor = %s;", (correo_alumno,))
     alumno_info = cursor.fetchone()

     cursor.close()

     if not alumno_info:
        return "Alumno no encontrado", 404

     return render_template('pages/progresoAlumno.html',alumno=alumno_info)

@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    # Obtener datos del formulario
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    email = request.form.get('email')

    cursor.execute("UPDATE Alumno SET Nombre=%s, Apellido=%s WHERE CorreoTutor=%s", (nombre, apellido, email))
    coneccion.commit()

    # Redirigir a la misma página después de actualizar
    return redirect(url_for('confAlumno'))

@app.route('/confAlumno')
def confAlumno():
    # Verificar que el usuario está logueado y tiene el rol de Tutor
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))

    # Obtener el correo del tutor desde la sesión
    correo_tutor = session['usuario'].get('CorreoTutor')

    if not correo_tutor:
        return redirect(url_for('inicioSesion'))

    cursor = coneccion.cursor(dictionary=True)

    # Obtener la información del alumno relacionado con el tutor
    cursor.execute("SELECT IdAlumno, Nombre, Apellido, Foto, CorreoTutor, IdGrupo FROM Alumno WHERE CorreoTutor = %s;", (correo_tutor,))
    alumno_info = cursor.fetchone()

    if not alumno_info:
        return "Alumno no encontrado", 404

    # Obtener el IdGrupo del alumno
    id_grupo = alumno_info.get('IdGrupo')

    if not id_grupo:
        return "El alumno no está asignado a ningún grupo", 404

    # Obtener la información del grupo para obtener el CorreoDocente
    cursor.execute("SELECT CorreoDocente FROM Grupo WHERE IdGrupo = %s;", (id_grupo,))
    grupo_info = cursor.fetchone()

    if not grupo_info:
        return "Grupo no encontrado", 404

    # Obtener la información del docente utilizando el CorreoDocente
    correo_docente = grupo_info.get('CorreoDocente')

    cursor.execute("SELECT Nombre, Apellido, CorreoDocente FROM Docente WHERE CorreoDocente = %s;", (correo_docente,))
    docente_info = cursor.fetchone()

    cursor.close()

    if not docente_info:
        return "Docente no encontrado", 404

    # Pasamos los datos del alumno y del docente a la plantilla
    return render_template('pages/confAlumno.html', alumno=alumno_info, docente=docente_info)

@app.route('/alumno')
def alumno():
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))
    
    correo_alumno = session['usuario']['CorreoTutor']

    cursor = coneccion.cursor(dictionary=True)
    
    # Obtener la información del alumno
    cursor.execute("SELECT IdAlumno, Nombre, Apellido, Foto, AciertosNumeros,AciertosLetras, IdGrupo, CorreoTutor FROM Alumno WHERE CorreoTutor = %s;", (correo_alumno,))
    alumno_info = cursor.fetchone()

    cursor.close()

    if not alumno_info:
        return "Alumno no encontrado", 404

    return render_template('pages/alumno.html', alumno=alumno_info)

@app.route('/salir_grupo', methods=['POST'])
def salir_grupo():
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))

    correo_tutor = session['usuario'].get('CorreoTutor')

    if not correo_tutor:
        return redirect(url_for('alumno', error="No se encontró el correo del tutor en la sesión"))

    cursor = coneccion.cursor(dictionary=True)

    # Obtener al alumno asociado al CorreoTutor del usuario en sesión
    cursor.execute("SELECT * FROM Alumno WHERE CorreoTutor = %s;", (correo_tutor,))
    alumno = cursor.fetchone()

    if not alumno:
        return redirect(url_for('alumno', error=f"No se encontró un alumno con el CorreoTutor: {correo_tutor}"))

    print(f"Alumno encontrado: {alumno}")

    # Obtener la información del grupo del alumno
    id_grupo = alumno.get('IdGrupo')

    if not id_grupo:
        return redirect(url_for('alumno', error="El alumno no está asignado a ningún grupo"))

    # Obtener la información del grupo
    cursor.execute("SELECT * FROM Grupo WHERE IdGrupo = %s;", (id_grupo,))
    grupo = cursor.fetchone()

    if not grupo:
        return redirect(url_for('alumno', error="No se encontró el grupo al que pertenece el alumno"))

    print(f"Grupo encontrado: {grupo}")

    # Eliminar la asignación del alumno al grupo
    cursor.execute("UPDATE Alumno SET IdGrupo = NULL, AciertosNumeros = 0, AciertosLetras = 0 WHERE CorreoTutor = %s;", (correo_tutor,))
    
    # Decrementar el número de alumnos en el grupo
    cursor.execute("UPDATE Grupo SET NoAlumnos = NoAlumnos - 1 WHERE IdGrupo = %s;", (id_grupo,))

    coneccion.commit()
    cursor.close()

    print(f"Alumno {alumno['Nombre']} ha salido del grupo {grupo['Titulo']}")

    return redirect(url_for('alumno'))  # Redirige a la vista de alumno

@app.route('/unirse_grupo', methods=['POST'])
def unirse_grupo():
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))

    codigo = request.form.get('codigo')

    if not codigo:
        return redirect(url_for('alumno', error="No se ingresó un código"))

    print(f"Código ingresado: {codigo}")

    cursor = coneccion.cursor(dictionary=True)

    # Obtener la información del grupo
    cursor.execute("SELECT * FROM Grupo WHERE Codigo = %s;", (codigo,))
    grupo = cursor.fetchone()

    if not grupo:
        return redirect(url_for('alumno', error="Código de grupo no válido"))

    print(f"Grupo encontrado: {grupo}")

    # Obtener al alumno asociado al CorreoTutor del usuario en sesión
    correo_tutor = session['usuario'].get('CorreoTutor')

    if not correo_tutor:
        return redirect(url_for('alumno', error="No se encontró el correo del tutor en la sesión"))

    cursor.execute("SELECT * FROM Alumno WHERE CorreoTutor = %s;", (correo_tutor,))
    alumno = cursor.fetchone()

    if not alumno:
        return redirect(url_for('alumno', error=f"No se encontró un alumno con el CorreoTutor: {correo_tutor}"))

    print(f"Alumno encontrado: {alumno}")

    # Actualizar el IdGrupo del alumno en la base de datos
    cursor.execute("UPDATE Alumno SET IdGrupo = %s WHERE CorreoTutor = %s;", (grupo['IdGrupo'], correo_tutor))
    cursor.execute("UPDATE Grupo SET NoAlumnos = NoAlumnos + 1 WHERE IdGrupo = %s;", (grupo['IdGrupo'],))
    coneccion.commit()
    print(f"Alumno {alumno['Nombre']} asignado al grupo {grupo['Titulo']}")

    return redirect(url_for('alumno'))  # Redirige a la vista de alumno

@app.route('/docente')
def docente():
    if 'usuario' not in session or session['usuario']['role'] != 'Docente':
        return redirect(url_for('inicioSesion'))

    correo_docente = session['usuario']['CorreoDocente']

    cursor = coneccion.cursor(dictionary=True)
    
    # Buscar la información del docente
    cursor.execute("SELECT Nombre, Apellido, CorreoDocente FROM Docente WHERE CorreoDocente = %s;", (correo_docente,))
    docente_info = cursor.fetchone()

    # Buscar el grupo vinculado al docente
    cursor.execute("SELECT IdGrupo, Titulo, Codigo, NoAlumnos FROM Grupo WHERE CorreoDocente = %s;", (correo_docente,))
    grupo = cursor.fetchone()
    return render_template('pages/docente.html', docente=docente_info, grupo=grupo)

@app.route('/confDocente')
def confDocente():
     return render_template('pages/confDocente.html')

@app.route('/dar_de_baja', methods=['GET'])
def dar_de_baja():
    if 'usuario' not in session or session['usuario']['role'] != 'Docente':
        return redirect(url_for('inicioSesion'))

    # Obtener el correo del alumno desde la consulta GET
    correo_alumno = request.args.get('correo_alumno')

    if not correo_alumno:
        return "Correo del alumno no proporcionado", 400
    
    cursor = coneccion.cursor(dictionary=True)

    # Obtener la información del alumno usando el correo proporcionado
    cursor.execute("""
        SELECT IdAlumno, Nombre, Apellido, Foto, AciertosNumeros, AciertosLetras, IdGrupo, CorreoTutor 
        FROM Alumno 
        WHERE CorreoTutor = %s
    """, (correo_alumno,))
    alumno_info = cursor.fetchone()

    if not alumno_info:
        cursor.close()
        return "Alumno no encontrado", 404

    # Guardar el IdGrupo del alumno para actualizarlo más tarde
    id_grupo = alumno_info['IdGrupo']

    # Actualiza el IdGrupo a NULL para dar de baja al alumno
    cursor.execute("""
        UPDATE Alumno 
        SET IdGrupo = NULL,
        AciertosNumeros = 0, 
        AciertosLetras = 0 
        WHERE CorreoTutor = %s
    """, (correo_alumno,))
    
    # Decrementar el número de alumnos en el grupo correspondiente
    if id_grupo is not None:
        cursor.execute("""
            UPDATE Grupo 
            SET NoAlumnos = NoAlumnos - 1
            WHERE IdGrupo = %s
        """, (id_grupo,))
    
    coneccion.commit()  # Realiza la transacción

    # Redirige al docente de vuelta a la lista de alumnos (ajustar según el nombre correcto de la ruta de alumnos)
    return redirect(url_for('listaAlumnos'))

@app.route('/progresoAlumnoDocente')
def progresoAlumnoDocente():
    if 'usuario' not in session or session['usuario']['role'] != 'Docente':
        return redirect(url_for('inicioSesion'))

    # Obtener el correo del alumno desde la consulta GET
    correo_alumno = request.args.get('correo_alumno')

    if not correo_alumno:
        return "Correo del alumno no proporcionado", 400
    
    cursor = coneccion.cursor(dictionary=True)

    # Obtener la información del alumno usando el correo proporcionado
    cursor.execute("""
        SELECT IdAlumno, Nombre, Apellido, Foto, AciertosNumeros, AciertosLetras, IdGrupo, CorreoTutor 
        FROM Alumno 
        WHERE CorreoTutor = %s
    """, (correo_alumno,))
    alumno_info = cursor.fetchone()
    if not alumno_info:
        return "Alumno no encontrado", 404

    return render_template('pages/progresoAlumnoDocente.html', alumno=alumno_info)

@app.route('/listaAlumnos')
def listaAlumnos():
    # Verificar si el usuario está autenticado y es un docente
    if 'usuario' not in session or session['usuario']['role'] != 'Docente':
        return redirect(url_for('inicioSesion'))

    correo_docente = session['usuario']['CorreoDocente']

    # Conectar a la base de datos usando el cursor que ya tenías definido
    cursor = coneccion.cursor(dictionary=True)
    
    # Obtener el grupo del docente
    cursor.execute("SELECT IdGrupo FROM Grupo WHERE CorreoDocente = %s;", (correo_docente,))
    grupo_info = cursor.fetchone()
    
    if not grupo_info:
        return render_template('pages/listaAlumnos.html', alumnos=[])

    # Obtener la lista de alumnos inscritos en el grupo
    cursor.execute("""
        SELECT A.IdAlumno, A.Nombre, A.CorreoTutor
        FROM Alumno A
        WHERE A.IdGrupo = %s;
    """, (grupo_info['IdGrupo'],))
    
    alumnos = cursor.fetchall()
    
    return render_template('pages/listaAlumnos.html', alumnos=alumnos)

@app.route('/eliminarGrupo', methods=['DELETE'])
def eliminar_grupo():
    print('eliminar grupo')  # Verificación para saber si se ejecuta esta ruta
    if 'usuario' not in session or session['usuario']['role'] != 'Docente':
        return redirect(url_for('inicioSesion'))

    correo_docente = session['usuario']['CorreoDocente']
    cursor = coneccion.cursor()
    cursor.execute("DELETE FROM Grupo WHERE CorreoDocente = %s", (correo_docente,))
    coneccion.commit()

    return jsonify({"success": True})

@app.route('/actualizarTitulo', methods=['POST'])
def actualizar_titulo():
    if 'usuario' not in session or session['usuario']['role'] != 'Docente':
        return jsonify({"error": "No autorizado"}), 403  # Mejor manejar errores con JSON

    data = request.get_json()  # 🔹 Obtener datos correctamente desde JSON
    nuevo_titulo = data.get('titulo')

    if not nuevo_titulo:
        return jsonify({"error": "Título no válido"}), 400

    correo_docente = session['usuario']['CorreoDocente']

    cursor = coneccion.cursor()
    cursor.execute("UPDATE Grupo SET Titulo = %s WHERE CorreoDocente = %s", (nuevo_titulo, correo_docente))
    coneccion.commit()
    cursor.close()

    return jsonify({"titulo": nuevo_titulo, "success": True})  # 🔹 Respuesta JSON

@app.route('/crearGrupo', methods=['POST'])
def crear_grupo():
    if 'usuario' not in session or session['usuario']['role'] != 'Docente':
        return redirect(url_for('inicioSesion'))

    correo_docente = session['usuario']['CorreoDocente']
    nombre_grupo = request.form.get('nombreGrupo')

    if not nombre_grupo:
        return redirect(url_for('docente'))  # Si no hay nombre, vuelve a la página

    codigo_unico = generar_codigo_unico()  # Generamos un código único

    cursor = coneccion.cursor()
    cursor.execute("INSERT INTO Grupo (Titulo, Codigo, NoAlumnos, CorreoDocente) VALUES (%s, %s, %s, %s)", 
                   (nombre_grupo, codigo_unico, 0, correo_docente))  # Guardamos el grupo con el código único
    coneccion.commit()
    cursor.close()

    return redirect(url_for('docente')) 

@app.route('/docente/info', methods=['GET'])
def getDocenteInfo():
     if 'usuario' not in session or session['usuario']['role'] != 'Docente':
          return jsonify({"error": "No autorizado"}), 401
     return jsonify(session['usuario'])

@app.route('/inicioSesion', methods=['POST'])
def inicioSesion():
    correo = request.form.get('email')
    contraseña = request.form.get('contraseña')
    hash = hashlib.sha256(contraseña.encode()).hexdigest()

    try:
        cursor = coneccion.cursor(dictionary=True)

        cursor.execute("SELECT CorreoTutor, 'Tutor' AS role FROM Tutor WHERE CorreoTutor=%s AND Contraseña=%s;", (correo, hash))
        usuario = cursor.fetchone()

        if not usuario:
            cursor.execute("SELECT CorreoDocente, Nombre, Apellido, 'Docente' AS role FROM Docente WHERE CorreoDocente=%s AND Contraseña=%s;", (correo, hash))
            usuario = cursor.fetchone()

        if not usuario:
            cursor.execute("SELECT CorreoAdministrador, 'Administrador' AS role FROM Administrador WHERE CorreoAdministrador=%s AND Contraseña=%s;", (correo, hash))
            usuario = cursor.fetchone()

        if usuario:
            session['usuario'] = usuario
            return jsonify({"status": "success", "role": usuario['role']})

        return jsonify({"status": "error", "message": "Correo o contraseña incorrectos, intenta de nuevo."}), 401

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": f"Error en la base de datos: {err}"}), 500

if __name__ == '__main__':
    app.run(port=8000,debug=True)
