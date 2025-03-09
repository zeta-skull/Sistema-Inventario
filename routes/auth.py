from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
from app import db, login_manager
from models.user import User, Role
from forms.auth import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm
from utils.decorators import admin_required
from utils.email import send_password_reset_email

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    """Carga el usuario para Flask-Login"""
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Vista de inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_active:
                login_user(user, remember=form.remember.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('inventory.dashboard'))
            else:
                flash('Esta cuenta ha sido desactivada. Por favor contacte al administrador.', 'danger')
        else:
            flash('Usuario o contraseña inválidos', 'danger')
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    """Vista de registro de usuario (solo admin)"""
    form = RegistrationForm()
    roles = Role.query.all()
    form.role.choices = [(role.id, role.name) for role in roles]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role_id=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash('¡Usuario creado exitosamente!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error. Por favor intente nuevamente.', 'danger')
    
    return render_template('auth/register.html', title='Registrar Usuario', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Vista de cierre de sesión"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Vista de cambio de contraseña"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('¡Su contraseña ha sido actualizada!', 'success')
            return redirect(url_for('inventory.dashboard'))
        else:
            flash('La contraseña actual es incorrecta', 'danger')
    return render_template('auth/change_password.html', title='Cambiar Contraseña', form=form)

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Vista de solicitud de restablecimiento de contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Revise su correo electrónico para obtener instrucciones sobre cómo restablecer su contraseña', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='Restablecer Contraseña', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Vista de restablecimiento de contraseña"""
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Su contraseña ha sido restablecida.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='Restablecer Contraseña', form=form)

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Vista de perfil de usuario"""
    return render_template('auth/profile.html', title='Perfil')
