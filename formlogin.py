from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField, Form, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired,Length,Email

class Formulario_Producto(Form):
    id = StringField('Id', [validators.DataRequired()])
    nombre = StringField('Nombre', [validators.DataRequired()])
    precio = StringField('Precio', [validators.DataRequired()])
    existencia = StringField('Existencia', [validators.DataRequired()])
    enviar = SubmitField('Agregar producto')

#CLASES
class formUsuarios(FlaskForm):
    correo = EmailField("Correo electronico", validators=[DataRequired(), Email()])
    contrasenia = PasswordField('Contraseña', validators=[DataRequired(), Length(min=3, max=20, message="La contraseña requiere entre %(min)d y %(max)d caracteres")])
    primerNombre = StringField('Pimer Nombre', validators=[DataRequired()])
    segundoNombre = StringField('Segundo Nombre', validators=[DataRequired()])
    Apellidos = StringField('Apellidos', validators=[DataRequired()])
    numDocumento = StringField('Documento', validators=[DataRequired()])
    telefono = StringField('Numero Telefonico', validators=[DataRequired()])
    direccion = StringField('Direccion', validators=[DataRequired()])
    registrar = SubmitField("Registrar Usuario")
    tipoUser = SelectField("Tipo Usuario ", validators=[DataRequired()])

class formLogin(FlaskForm):
    # nombre = StringField('Nombre', validators=[DataRequired(message='No dejar vacío, completar')])
    email = EmailField("Correo electronico", validators=[DataRequired(message='Campo Requerido *'), Email()])
    password = PasswordField("Password", validators=[DataRequired(message='Campo Requerido *'), Length(min=3, max=20, message="La contraseña requiere entre %(min)d y %(max)d caracteres")])
    recaptcha = RecaptchaField()
    enviar = SubmitField("Iniciar Sesión")

class formMaterias(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), validators.Length(max=50, message="El nombre requiere maximo %(max)d caracteres"), validators.Regexp('[a-zA-Z]', message="Solo Letras")])
    descripcion = StringField('Descripción', validators=[DataRequired(), validators.Length(min=20, max=150, message="La descripcion debe tener entre %(min)d y %(max)d caracteres")])
    registrar = SubmitField('Registrar')

