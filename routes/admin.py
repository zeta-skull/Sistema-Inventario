from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models.user import User, Role
from utils.decorators import admin_required
from forms.auth import RegistrationForm
import os
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Panel de control de administración"""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    roles = Role.query.all()
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         active_users=active_users,
                         roles=roles)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """Gestión de usuarios"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/user/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    """Activar/desactivar usuario"""
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('¡No puede desactivar su propia cuenta!', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activado' if user.is_active else 'desactivado'
    flash(f'Usuario {user.username} ha sido {status}!', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """Editar usuario"""
    user = User.query.get_or_404(id)
    form = RegistrationForm(obj=user)
    roles = Role.query.all()
    form.role.choices = [(role.id, role.name) for role in roles]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('¡Usuario actualizado exitosamente!', 'success')
        return redirect(url_for('admin.users'))
        
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/admin/roles')
@login_required
@admin_required
def roles():
    """Gestión de roles"""
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles)

@admin_bp.route('/admin/role/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_role():
    """Agregar nuevo rol"""
    if request.method == 'POST':
        name = request.form.get('name')
        permissions = {
            'user_manage': 'user_manage' in request.form,
            'inventory_manage': 'inventory_manage' in request.form,
            'reports_view': 'reports_view' in request.form,
            'settings_manage': 'settings_manage' in request.form
        }
        
        role = Role(name=name, permissions=permissions)
        db.session.add(role)
        db.session.commit()
        flash('¡Rol agregado exitosamente!', 'success')
        return redirect(url_for('admin.roles'))
        
    return render_template('admin/role_form.html', title='Agregar Rol')

@admin_bp.route('/admin/role/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(id):
    """Editar rol"""
    role = Role.query.get_or_404(id)
    
    if request.method == 'POST':
        role.name = request.form.get('name')
        role.permissions = {
            'user_manage': 'user_manage' in request.form,
            'inventory_manage': 'inventory_manage' in request.form,
            'reports_view': 'reports_view' in request.form,
            'settings_manage': 'settings_manage' in request.form
        }
        db.session.commit()
        flash('¡Rol actualizado exitosamente!', 'success')
        return redirect(url_for('admin.roles'))
        
    return render_template('admin/role_form.html', role=role, title='Editar Rol')

@admin_bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """Configuración del sistema"""
    if request.method == 'POST':
        # Actualizar configuración del sistema
        settings = {
            'company_name': request.form.get('company_name'),
            'email_notifications': 'email_notifications' in request.form,
            'low_stock_threshold': request.form.get('low_stock_threshold'),
            'theme': request.form.get('theme')
        }
        
        # Guardar configuración en archivo o base de datos
        with open('config/settings.json', 'w') as f:
            json.dump(settings, f)
            
        # Manejar carga de logo
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo.filename:
                filename = secure_filename(logo.filename)
                logo.save(os.path.join('static', 'images', filename))
                settings['logo'] = filename
                
        flash('¡Configuración actualizada exitosamente!', 'success')
        return redirect(url_for('admin.settings'))
        
    # Cargar configuración actual
    try:
        with open('config/settings.json', 'r') as f:
            settings = json.load(f)
    except:
        settings = {
            'company_name': '',
            'email_notifications': True,
            'low_stock_threshold': 10,
            'theme': 'light',
            'logo': None
        }
        
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/admin/backup', methods=['POST'])
@login_required
@admin_required
def backup_database():
    """Crear respaldo de base de datos"""
    try:
        # Crear directorio de respaldo si no existe
        os.makedirs('backups', exist_ok=True)
        
        # Generar nombre de archivo con marca de tiempo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backups/inventario_backup_{timestamp}.sql'
        
        # Ejecutar comando de respaldo
        os.system(f'sqlite3 instance/inventory.db .dump > {backup_file}')
        
        flash('¡Respaldo de base de datos creado exitosamente!', 'success')
    except Exception as e:
        flash(f'Error en respaldo: {str(e)}', 'danger')
        
    return redirect(url_for('admin.settings'))

@admin_bp.route('/admin/restore/<filename>', methods=['POST'])
@login_required
@admin_required
def restore_database(filename):
    """Restaurar base de datos desde respaldo"""
    try:
        backup_file = os.path.join('backups', filename)
        if os.path.exists(backup_file):
            # Ejecutar comando de restauración
            os.system(f'sqlite3 instance/inventory.db < {backup_file}')
            flash('¡Base de datos restaurada exitosamente!', 'success')
        else:
            flash('¡Archivo de respaldo no encontrado!', 'danger')
    except Exception as e:
        flash(f'Error en restauración: {str(e)}', 'danger')
        
    return redirect(url_for('admin.settings'))
