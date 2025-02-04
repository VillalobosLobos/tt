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

@app.route('/alumno')
def alumno():
    if 'usuario' not in session or session['usuario']['role'] != 'Tutor':
        return redirect(url_for('inicioSesion'))
    
    correo_alumno = session['usuario']['CorreoTutor']

    cursor = coneccion.cursor(dictionary=True)
    
    # Obtener la información del alumno
    cursor.execute("SELECT IdAlumno, Nombre, Apellido, Foto, Aciertos, IdGrupo, CorreoTutor FROM Alumno WHERE CorreoTutor = %s;", (correo_alumno,))
    alumno_info = cursor.fetchone()

    cursor.close()

    if not alumno_info:
        return "Alumno no encontrado", 404

    return render_template('pages/alumno.html', alumno=alumno_info)

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
