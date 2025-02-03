from mysql.connector.errors import IntegrityError
from flask import Flask, request,render_template,jsonify, session
from mysql.connector.errors import IntegrityError
from flask_session import Session
from mysql.connector import Error
from flask import jsonify
import mysql.connector

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

@app.route('/')
def index():
	return render_template('index.html')

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
     return render_template('pages/alumno.html')

@app.route('/docente')
def docente():
     return render_template('pages/docente.html')

@app.route('/docente/info', methods=['GET'])
def getDocenteInfo():
     if 'usuario' not in session or session['usuario']['role'] != 'Docente':
          return jsonify({"error": "No autorizado"}), 401
     return jsonify(session['usuario'])

@app.route('/inicioSesion',methods=['POST'])
def inicioSesion():
    correo=request.form.get('email')
    contraseña=request.form.get('contraseña')

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
