from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """Modelo para usuarios del sistema"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        """Establece la contraseña encriptada del usuario"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña del usuario"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Role(db.Model):
    """Modelo para roles de usuario"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    permissions = db.Column(db.JSON)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Rol {self.name}>'

# Definir roles y permisos predeterminados
ROLES_PREDETERMINADOS = {
    'admin': {
        'name': 'Administrador',
        'permissions': {
            'user_manage': True,      # Gestionar usuarios
            'inventory_manage': True,  # Gestionar inventario
            'reports_view': True,      # Ver reportes
            'settings_manage': True    # Gestionar configuración
        }
    },
    'manager': {
        'name': 'Gerente',
        'permissions': {
            'user_manage': False,      # No puede gestionar usuarios
            'inventory_manage': True,  # Puede gestionar inventario
            'reports_view': True,      # Puede ver reportes
            'settings_manage': False   # No puede gestionar configuración
        }
    },
    'staff': {
        'name': 'Personal',
        'permissions': {
            'user_manage': False,      # No puede gestionar usuarios
            'inventory_manage': True,  # Puede gestionar inventario
            'reports_view': False,     # No puede ver reportes
            'settings_manage': False   # No puede gestionar configuración
        }
    }
}
