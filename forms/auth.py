from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User

class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    """Formulario de registro de usuario"""
    username = StringField('Usuario', validators=[
        DataRequired(), 
        Length(min=4, max=20, message='El usuario debe tener entre 4 y 20 caracteres')
    ])
    email = StringField('Correo Electrónico', validators=[
        DataRequired(), 
        Email(message='Por favor ingrese un correo electrónico válido')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    role = SelectField('Rol', choices=[
        ('staff', 'Personal'), 
        ('manager', 'Gerente')
    ], validators=[DataRequired()])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        """Valida que el nombre de usuario no exista"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso. Por favor elija otro.')

    def validate_email(self, email):
        """Valida que el correo electrónico no esté registrado"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este correo electrónico ya está registrado. Por favor use otro.')

class ChangePasswordForm(FlaskForm):
    """Formulario de cambio de contraseña"""
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(),
        EqualTo('new_password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Cambiar Contraseña')

class ResetPasswordRequestForm(FlaskForm):
    """Formulario de solicitud de restablecimiento de contraseña"""
    email = StringField('Correo Electrónico', validators=[
        DataRequired(),
        Email(message='Por favor ingrese un correo electrónico válido')
    ])
    submit = SubmitField('Solicitar Restablecimiento')

class ResetPasswordForm(FlaskForm):
    """Formulario de restablecimiento de contraseña"""
    password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Restablecer Contraseña')
