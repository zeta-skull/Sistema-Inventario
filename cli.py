import click
from flask.cli import with_appcontext
from app import app, db
from models.user import User, Role
from werkzeug.security import generate_password_hash
import os
from datetime import datetime, timedelta
import shutil

@app.cli.command("create-admin")
@click.option('--username', default='admin', help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin(username, email, password):
    """Crear un usuario administrador"""
    try:
        # Crear rol de administración si no existe
        admin_role = Role.query.filter_by(name='Administrator').first()
        if not admin_role:
            admin_role = Role(
                name='Administrator',
                permissions={
                    'user_manage': True,
                    'inventory_manage': True,
                    'reports_view': True,
                    'settings_manage': True
                }
            )
            db.session.add(admin_role)
            db.session.commit()

        # Comprueba si el usuario administrador ya existe
        if User.query.filter_by(username=username).first():
            click.echo('¡El usuario administrativo ya existe!')
            return

        # Crear usuario administrador
        admin = User(
            username=username,
            email=email,
            role_id=admin_role.id,
            is_active=True
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo('¡Usuario administrador creado con éxito!')

    except Exception as e:
        click.echo(f'Error a crear usuario administrador: {str(e)}')
        db.session.rollback()

@app.cli.command("init-db")
@with_appcontext
def init_db():
    """Inicializar la base de datos"""
    try:
        db.create_all()
        click.echo('¡Base de datos inicializada con éxito!')

        # Crear roles predeterminados
        roles = [
            {
                'name': 'Administrador',
                'permissions': {
                    'user_manage': True,
                    'inventory_manage': True,
                    'reports_view': True,
                    'settings_manage': True
                }
            },
            {
                'name': 'Gerente',
                'permissions': {
                    'user_manage': False,
                    'inventory_manage': True,
                    'reports_view': True,
                    'settings_manage': False
                }
            },
            {
                'name': 'Personal',
                'permissions': {
                    'user_manage': False,
                    'inventory_manage': True,
                    'reports_view': False,
                    'settings_manage': False
                }
            }
        ]

        for role_data in roles:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(**role_data)
                db.session.add(role)

        db.session.commit()
        click.echo('¡Roles predeterminados creados con éxito!')

    except Exception as e:
        click.echo(f'Error de inicialización de la base de datos: {str(e)}')
        db.session.rollback()

@app.cli.command("backup-db")
@click.option('--output', default=None, help='Output directory for backup')
@with_appcontext
def backup_db():
    """Crear una copia de seguridad de la base de datos"""
    try:
        # Crear directorio de respaldo si no existe
        backup_dir = os.getenv('BACKUP_FOLDER', 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Genere el nombre de archivo de respaldo con marca de tiempo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'inventory_backup_{timestamp}.sql'
        backup_path = os.path.join(backup_dir, backup_file)

        # Ejecutar el comando de copia de seguridad
        os.system(f'sqlite3 instance/inventory.db .dump > {backup_path}')
        click.echo(f'Database backup created: {backup_path}')

        # Copias de seguridad viejas limpias
        retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
        cleanup_old_backups(backup_dir, retention_days)

    except Exception as e:
        click.echo(f'Error creating backup: {str(e)}')

@app.cli.command("restore-db")
@click.argument('backup_file')
@with_appcontext
def restore_db(backup_file):
    """Restaurar la base de datos desde la copia de seguridad"""
    try:
        if not os.path.exists(backup_file):
            click.echo('Archivo de copia de seguridad no encontrado!')
            return

        # Crear una copia de seguridad antes de restaurar
        backup_db()

        # Restaurar base de datos
        os.system(f'sqlite3 instance/inventory.db < {backup_file}')
        click.echo('¡Base de datos restaurada con éxito!')

    except Exception as e:
        click.echo(f'Error de restaurar la base de datos: {str(e)}')

@app.cli.command("cleanup-files")
@click.option('--days', default=7, help='Eliminar archivos más antiguos que los días especificados')
@with_appcontext
def cleanup_files(days):
    """Limpiar archivos temporales antiguos"""
    try:
        # Limpiar informes antiguos
        cleanup_directory('reports', days)
        
        # Limpiar las cargas antiguas
        cleanup_directory('static/uploads', days)
        
        click.echo('¡Limpieza de archivos completada con éxito!')

    except Exception as e:
        click.echo(f'Error durante la limpieza: {str(e)}')

def cleanup_directory(directory, days):
    """Limpiar archivos en un directorio más antiguo que los días especificados"""
    if not os.path.exists(directory):
        return

    cutoff_date = datetime.now() - timedelta(days=days)
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_modified < cutoff_date:
                os.remove(filepath)

def cleanup_old_backups(backup_dir, retention_days):
    """Limpiar archivos de copia de seguridad más antiguos que el período de retención"""
    if not os.path.exists(backup_dir):
        return

    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    for filename in os.listdir(backup_dir):
        if filename.startswith('inventory_backup_') and filename.endswith('.sql'):
            filepath = os.path.join(backup_dir, filename)
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_modified < cutoff_date:
                os.remove(filepath)

if __name__ == '__main__':
    app.cli()