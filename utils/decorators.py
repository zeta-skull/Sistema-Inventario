from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(roles):
    """
    Decorador para requerir roles específicos para acceder a una ruta.
    
    Args:
        roles (list): Lista de nombres de roles permitidos
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # No autorizado
            if current_user.role.name not in roles:
                abort(403)  # Prohibido
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorador para requerir rol de administrador para acceder a una ruta.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'Administrador':
            abort(403)  # Prohibido
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """
    Decorador para requerir rol de gerente o superior para acceder a una ruta.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or \
           current_user.role.name not in ['Administrador', 'Gerente']:
            abort(403)  # Prohibido
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """
    Decorador para verificar que el usuario esté activo.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_active:
            abort(403)  # Prohibido
        return f(*args, **kwargs)
    return decorated_function
