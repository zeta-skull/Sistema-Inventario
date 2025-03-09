from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar aplicación Flask
app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventario.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-clave-secreta')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Configuración de correo
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager(app)
jwt = JWTManager(app)
mail = Mail(app)

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Importar y registrar blueprints
from routes.auth import auth_bp
from routes.inventory import inventory_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(admin_bp)

# Manejador de errores 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# Manejador de errores 500
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Endpoint de verificación de salud
@app.route('/health')
def health_check():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
