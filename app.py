#Importar librerias, clases, Dependencias etc...
import os
from sqlite3 import Error
from flask import Flask, render_template, request, flash, session
from flask.helpers import url_for
from flask_wtf import RecaptchaField
from werkzeug.utils import redirect
import bcrypt
import smtplib

# Flask-wtf
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError, DataRequired, Length

from conexion import get_db, close_db
from formlogin import formUsuarios, formLogin, formMaterias

#Resolver problemas de codifiacion
import importlib,sys
importlib.reload(sys)

#Objeto app de la clase Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfXH_McAAAAAKytGfXrdqWIq5_HIWO5T0jSsZ5p'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfXH_McAAAAAJ7F3pmteXdxYLnqc_lcU9-6oDTT'
app.config['TESTING'] = False

#Semilla Para Encriptar se usa en  /registroUser
semilla = bcrypt.gensalt()


#Creacion de rutas y metodos HTTP

#Ruta -----------  Index Pagina Inicial
@app.route('/index')
@app.route('/')
def index():
     return render_template("index.html")

# Ruta ----------- Login
@app.route('/login', methods=['GET', 'POST'])
def login():
     form = formLogin()
     if (request.method == "POST"):
          email = request.form['email']
          password = request.form['password']

          password_encode = password.encode("utf-8")

          if form.validate_on_submit():

            db = get_db()
            cur = db.cursor()

            sQuery = "SELECT idUsuario,correo,contrasenia,primerNombre,segundoNombre,Apellidos,numDocumento,telefono,direccion,idTipoUsuario FROM usuario WHERE correo = ?"

            cur.execute(sQuery,[email])

            user = cur.fetchone()

            cur.close()

            if user is None: 
                db = close_db()
                form.email.data = ""
                error = 'Usuario o contraseña inválidos'
                flash( error )
            else:
                password_encriptado_encode = user[2]

                if bcrypt.checkpw(password_encode,password_encriptado_encode):
                    if user[9] == 1:
                        session["usuario"] = email
                        session["nivel"] = "administrador"
                        return redirect("/admin")
                    elif user[9] == 2:
                        session["usuario"] = email 
                        session["nivel"] = "docente"
                        return render_template("docente/main.html", usuario = user)
                    elif user[9] == 3:
                        session["usuario"] = email 
                        session["nivel"] = "estudiante"
                        return redirect("/estudiante")
                else:
                    form.email.data = ""
                    flash("Contraseña Incorrecta")
            
            return render_template("login.html", form=form)
            
          else:
              
              return render_template("login.html", form=form)
     
     return render_template("login.html", form=form)

# Rutas ------     CONTROL ACCESO

@app.route('/admin', methods=["GET",'POST'])
def irAdmin():
    return render_template("superadmin/main.html")

@app.route('/docente', methods=['GET','POST'])
def irDocente():
    return render_template("docente/main.html")

@app.route('/estudiante', methods=['GET','POST'])
def irEstudiante():
    return render_template("estudiante/main.html")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect("/")


#Rutas -------- REGISTO TABLA USUARIO
@app.route('/registroUser', methods=['GET', 'POST'])
def registroUser():
    form = formUsuarios(request.form)
    if (request.method == 'GET'):
        if 'usuario' in session:
            cursor = get_db().cursor()
            cursor.execute('SELECT idTipoUsuario,nombre,descripcion FROM tipoUsuario')
            tipoUser = cursor.fetchall()
            cursor.close()
            return render_template("superadmin/registrarusuarios.html", form=form, tipoUser=tipoUser)
        else:
            return redirect("/")
    else:
        # POST y capturamos los datos del formulario:
        correo = request.form['correo'].strip().lower()

        contrasenia = request.form['contrasenia'].strip()
        #Encriptar contraseña usando semilla 
        password_encode = contrasenia.encode("utf-8")
        password_encriptada = bcrypt.hashpw(password_encode,semilla)

        primerNombre = request.form['primerNombre'].strip().lower()
        segundoNombre = request.form['segundoNombre'].strip().lower()
        Apellidos = request.form['Apellidos'].strip().lower()
        numDocumento = request.form['numDocumento'].strip().lower()
        telefono = request.form['telefono'].strip().lower()
        direccion = request.form['direccion'].strip().lower()
        tipoUser = request.form['tipoUser']

        try:
            sQuery = "INSERT INTO usuario (correo,contrasenia,primerNombre,segundoNombre,Apellidos,numDocumento,telefono,direccion,idTipoUsuario) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        
            con = get_db()
            cur = con.cursor()
            cur.execute(sQuery,(correo,password_encriptada,primerNombre,segundoNombre,Apellidos,numDocumento,telefono,direccion,tipoUser))
            con.commit()
            con.close()
            error = ""
            if cur is None:
                error = "Error en el registro"
                flash(error,'error')
            else:
                error ="Registro de Usuario Exitoso"
                flash(error, 'success')
                return redirect("/registroUser")
                
            return error
        
        except Error:
            print( Error)
    

@app.route('/consultarUsers')
def consultarUsers():
    db = get_db()
    cur = db.cursor()

    sQuery = "SELECT * FROM usuario"

    cur.execute(sQuery)

    data = cur.fetchall()

    cur.close()
    # if (request.method == 'GET'):
    #     if 'usuario' in session:
    #         cursor = get_db().cursor()
    #         cursor.execute('SELECT idTipoUsuario,nombre,descripcion FROM tipoUsuario')
    #         tipoUser = cursor.fetchall()
    #         cursor.close()
    return render_template("superadmin/consultarUser.html", usuarios = data)
    #     else:
    #         return redirect("/")
    # else:

# ------------------ RUTA EDITAR TABLA USUARIOS
@app.route('/editUser/<id>', methods=['GET','POST'])
def editUser(id):
    db = get_db() #Abre conexion
    cur = db.cursor() #Variable que tiene la conexion y cre un objeto de tipo cursor

    sQuery = "SELECT * FROM usuario WHERE idUsuario = ?" # sentencia SQL
    cur.execute(sQuery,[id]) #Preparamos la sentencia para ejecucion

    userEdit = cur.fetchone()
    cur.close() # cerramos el cursor
    return render_template("superadmin/editarUser.html" , usuario = userEdit)


# ------------------ RUTA ACTUALIZAR TABLA USUARIOS
@app.route('/updateUser/<id>', methods = ['POST'])
def updateUser(id):

    if request.method == 'POST':
        #Captura de datos
        correo = request.form['correo']
        password = request.form['password']

        primerNombre = request.form['primerNombre']
        segundoNombre = request.form['segundoNombre']
        apellidos = request.form['apellidos']
        numDocumento = request.form['numDocumento']
        telefono = request.form['telefono']
        direccion = request.form['direccion']

        #Encriptar contraseña usando semilla 
        password_encode = password.encode("utf-8")
        password_encriptada = bcrypt.hashpw(password_encode,semilla)

        db = get_db() #Abre conexion
        cur = db.cursor() #Variable que tiene la conexion y cre un objeto de tipo cursor

        sQuery = """UPDATE usuario
                    SET correo = ?,
                        contrasenia = ?,
                        primerNombre = ?,
                        segundoNombre = ?,
                        Apellidos = ?,
                        numDocumento = ?,
                        telefono = ?,
                        direccion = ?
                    WHERE idUsuario = ?""" 

        # sentencia SQL
        cur.execute(sQuery,(correo,password_encriptada,primerNombre,segundoNombre,apellidos,numDocumento,telefono,direccion,id)) #Preparamos la sentencia para ejecucion
        db.commit()
        cur.close() # cerramos el cursor
        db = close_db()
        return redirect(url_for("consultarUsers"))

# ------------------ RUTA ELIMINAR TABLA USUARIOS
@app.route('/deleteUser/<string:id>')
def deleteUser(id):
    try:
        db = get_db()
        cur = db.cursor()
        sQuery = "DELETE FROM usuario WHERE idUsuario = {0}".format(id)
        cur.execute(sQuery)
        flash("Eliminado Satisfactoriamente") # falta incluir mensaje
        db.commit()
        cur.close()
        db.close()
    except Error:
            print( Error)
            flash("Se ha detectado un error al intentar eliminar el registro")
    finally:
        return redirect(url_for('consultarUsers'))

# ------------------------------- RUTA REGISTRO MATERIAS
@app.route('/registromateria', methods=['GET','POST'])
def registromateria():
    forMateria = formMaterias()
    if (request.method == 'GET'):
        if 'usuario' in session:
            return render_template("/superadmin/RegisMat.html", form=forMateria)
        else:
            return redirect("/")
    else:
        if forMateria.validate_on_submit():
            nombre = request.form['nombre'].strip().lower()
            descripcion = request.form['descripcion'].strip().lower()
            try:
                sQuery = "INSERT INTO materias (nombre,descripcion) VALUES (?,?)"
                con = get_db()
                cur = con.cursor()
                cur.execute(sQuery,(nombre,descripcion))
                con.commit()
                con.close()
                error = ""
                if cur is None:
                    error = "Error en el registro"
                    flash(error,'error')
                else:
                    error ="Registro de Usuario Exitoso"
                    flash(error, 'success')
                    return redirect("/registromateria")

                return error

            except Error:
                print(Error)

        return render_template('/superadmin/RegisMat.html', form=forMateria)

#-------------------------------- RUTA CONSULTAR MATERIAS
@app.route('/consultarMat')
def consultarMat():
    db = get_db()
    cur = db.cursor()

    sQuery = "SELECT * FROM materias"

    cur.execute(sQuery)

    data = cur.fetchall()

    cur.close()
    # if (request.method == 'GET'):
    #     if 'usuario' in session:
    #         cursor = get_db().cursor()
    #         cursor.execute('SELECT idTipoUsuario,nombre,descripcion FROM tipoUsuario')
    #         tipoUser = cursor.fetchall()
    #         cursor.close()
    return render_template("superadmin/consultarMat.html", materias = data)
    #     else:
    #         return redirect("/")
    # else:

# ------------------ RUTA EDITAR MATERIA
@app.route('/editMat/<id>', methods=['GET','POST'])
def editMat(id):
    db = get_db() #Abre conexion
    cur = db.cursor() #Variable que tiene la conexion y cre un objeto de tipo cursor

    sQuery = "SELECT * FROM materias WHERE idMateria = ?" # sentencia SQL
    cur.execute(sQuery,[id]) #Preparamos la sentencia para ejecucion

    materiaEdit = cur.fetchone()
    cur.close() # cerramos el cursor
    return render_template("superadmin/editarMat.html" , materia = materiaEdit)


# ------------------ RUTA ACTUALIZAR MATERIA
@app.route('/updateMat/<id>', methods = ['POST'])
def updateMat(id):

    if request.method == 'POST':
        #Captura de datos
        nombre = request.form['nombre'].strip().lower()
        descripcion = request.form['descripcion'].strip().lower()

        db = get_db() #Abre conexion
        cur = db.cursor() #Variable que tiene la conexion y cre un objeto de tipo cursor

        sQuery = """UPDATE materias
                        SET nombre = ?,
                            descripcion = ?
                    WHERE idMateria = ?""" 

        # sentencia SQL
        cur.execute(sQuery,(nombre,descripcion,id)) #Preparamos la sentencia para ejecucion
        db.commit()
        cur.close() # cerramos el cursor
        db = close_db()
        return redirect(url_for("consultarMat"))
        

# ------------------ RUTA ELIMINAR MATERIAS
@app.route('/deleteMat/<string:id>')
def deleteMat(id):
    try:
        db = get_db()
        cur = db.cursor()
        sQuery = "DELETE FROM materias WHERE idMateria = {0}".format(id)
        cur.execute(sQuery)
        flash("Eliminado Satisfactoriamente") # falta incluir mensaje
        db.commit()
        cur.close()
        db = close_db()
    except Error:
            print( Error)
            flash("Se ha detectado un error al intentar eliminar el registro")
    finally:
        return redirect(url_for('consultarMat'))


# ------------------ RUTA CONSULTAR INFORMACION DOCENTE
@app.route('/miInformacion/<id>', methods=['GET','POST'])
def miInformacion(id):
    db = get_db() #Abre conexion
    cur = db.cursor() #Variable que tiene la conexion y cre un objeto de tipo cursor

    sQuery = "SELECT * FROM usuario WHERE idUsuario = ?" # sentencia SQL
    cur.execute(sQuery,[id]) #Preparamos la sentencia para ejecucion

    userInfo = cur.fetchone()
    cur.close()
    if userInfo is None: 
        error = 'No se Encontro Informac'
        flash( error )
    else:
        return render_template("docente/misDatos.html" , usuario = userInfo)

@app.route('/form', methods=['POST'])
def form():
    primer_nombre = request.form.get("primer_nombre")
    segundo_nombre = request.form.get("segundo_nombre")
    email = request.form.get("email")
    
    message = "Se te ha dado de alta en el sistema"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("bastosy@uninorte.edu.co", "")
    server.sendmail("bastosy@uninorte.edu.co",email,message)

    if not primer_nombre or not segundo_nombre or not email:
        error_statement = "Todos los campos requeridos"
        return render_template("superadmin/main.html", error_statement=error_statement, primer_nombre=primer_nombre, segundo_nombre=segundo_nombre,email=email)
    return render_template("superadmin/main.html")


#------------------------- ELIMINAR ES SOLO DE PRUEBA
@app.route('/table')
def pruebatable():
    return render_template("table.html")
    

# Un "middleware" que se ejecuta antes de responder a cualquier ruta. Aquí verificamos si el usuario ha iniciado sesión
@app.before_request
def antes_de_cada_ruta():
    ruta = request.path
    # Si no ha iniciado sesión y no quiere ir a algo relacionado al login, lo redireccionamos al login
    if not 'usuario' in session and ruta != "/login" and ruta != "/" and ruta != "/logout" and not ruta.startswith("/static"):
        flash("Inicia sesión para continuar")
        return redirect("/login")
    # Si ya ha iniciado, no hacemos nada, es decir lo dejamos pasar

if  __name__ == "__main__":
    os.environ['FLASK_ENV'] = 'development'
    app.run(port=3000, debug=True)