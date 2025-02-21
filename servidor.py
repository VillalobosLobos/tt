from mysql.connector.errors import IntegrityError
from flask import Flask, request,render_template,jsonify, session,redirect, url_for
from mysql.connector.errors import IntegrityError
from flask_session import Session
from mysql.connector import Error
from flask import jsonify
import mysql.connector
import random
import string

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
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = './flask_session'
Session(app)

def generar_codigo_unico():
    """ Genera un código aleatorio de 5 caracteres y verifica que no esté en la base de datos. """
    while True:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))  # Ej: "A1B2C"
        cursor = coneccion.cursor()
        cursor.execute("SELECT Codigo FROM Grupo WHERE Codigo = %s;", (codigo,))
        resultado = cursor.fetchone()
        cursor.close()

        if not resultado:  # Si el código no está en la BD, es único y lo usamos
            return codigo

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

@app.route('/recuperarContraseña')
def recuperarContraseña():
     return render_template('pages/recuperarContraseña.html')

@app.route('/crearCuenta')
def crearCuenta():
     return render_template('pages/crearCuenta.html')

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
    cursor.execute("UPDATE Alumno SET IdGrupo = NULL WHERE CorreoTutor = %s;", (correo_tutor,))
    
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
    cursor.close()

    print(f"Alumno {alumno['Nombre']} asignado al grupo {grupo['Titulo']}")

    return redirect(url_for('alumno'))  # Redirige a la vista de alumno

@app.route('/docente')
def docente():
    if 'usuario' not in session or session['usuario']['role'] != 'Docente':
        return redirect(url_for('inicioSesion'))

    correo_docente = session['usuario']['CorreoDocente']

    cursor = coneccion.cursor(dictionary=True)
    
    # Buscar la información del docente
    cursor.execute("SELECT Nombre, Apellido FROM Docente WHERE CorreoDocente = %s;", (correo_docente,))
    docente_info = cursor.fetchone()

    # Buscar el grupo vinculado al docente
    cursor.execute("SELECT IdGrupo, Titulo, Codigo, NoAlumnos FROM Grupo WHERE CorreoDocente = %s;", (correo_docente,))
    grupo = cursor.fetchone()

    cursor.close()

    return render_template('pages/docente.html', docente=docente_info, grupo=grupo)

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

@app.route('/inicioSesion',methods=['POST'])
def inicioSesion():
    correo=request.form.get('email')
    contraseña=request.form.get('contraseña')

    #print(f'{contraseña} y {correo}')

    cursor=coneccion.cursor(dictionary=True)

    #Por si es un tutor
    cursor.execute("SELECT CorreoTutor, 'Tutor' AS role FROM Tutor WHERE CorreoTutor=%s AND Contraseña=%s;", (correo, contraseña))
    usuario = cursor.fetchone()

    if not usuario:
         cursor.execute("SELECT CorreoDocente, Nombre, Apellido, 'Docente' AS role FROM Docente WHERE CorreoDocente=%s AND Contraseña=%s;", (correo, contraseña))
         usuario=cursor.fetchone()
     
    cursor.close() 

    if usuario:
         session['usuario']=usuario
         return jsonify({"status": "success", "role": usuario['role']})

    return jsonify({"status": "error", "message": "Correo o contraseña incorrectos, intenta de nuevo."}), 401

if __name__ == '__main__':
    app.run(port=8000,debug=True)
