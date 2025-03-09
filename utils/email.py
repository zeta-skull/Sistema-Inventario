from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    """
    Envía un correo electrónico de forma asíncrona.
    
    Args:
        app: Aplicación Flask
        msg: Objeto Message de Flask-Mail
    """
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, text_body, html_body):
    """
    Función general para enviar correos electrónicos.
    
    Args:
        subject: Asunto del correo
        recipients: Lista de destinatarios
        text_body: Contenido en texto plano
        html_body: Contenido en HTML
    """
    msg = Message(subject, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    """
    Envía correo de restablecimiento de contraseña.
    
    Args:
        user: Objeto Usuario
    """
    token = user.get_reset_password_token()
    send_email(
        '[Sistema de Inventario] Restablecer Contraseña',
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt',
                                user=user, token=token),
        html_body=render_template('email/reset_password.html',
                                user=user, token=token)
    )

def send_stock_alert(product):
    """
    Envía alerta cuando el stock de un producto está bajo.
    
    Args:
        product: Objeto Producto
    """
    from models.user import User, Role
    
    # Obtener todos los usuarios admin y gerentes
    admin_role = Role.query.filter_by(name='Administrador').first()
    manager_role = Role.query.filter_by(name='Gerente').first()
    recipients = User.query.filter(
        User.role_id.in_([admin_role.id, manager_role.id]),
        User.is_active == True
    ).with_entities(User.email).all()
    
    if not recipients:
        return
        
    send_email(
        '[Alerta de Inventario] Notificación de Stock Bajo',
        recipients=[email[0] for email in recipients],
        text_body=render_template('email/stock_alert.txt',
                                product=product),
        html_body=render_template('email/stock_alert.html',
                                product=product)
    )

def send_welcome_email(user):
    """
    Envía correo de bienvenida a nuevos usuarios.
    
    Args:
        user: Objeto Usuario
    """
    send_email(
        'Bienvenido al Sistema de Gestión de Inventario',
        recipients=[user.email],
        text_body=render_template('email/welcome.txt',
                                user=user),
        html_body=render_template('email/welcome.html',
                                user=user)
    )

def send_daily_report(report_data):
    """
    Envía reporte diario de inventario a administradores.
    
    Args:
        report_data: Diccionario con datos del reporte
    """
    from models.user import User, Role
    
    admin_role = Role.query.filter_by(name='Administrador').first()
    recipients = User.query.filter_by(
        role_id=admin_role.id,
        is_active=True
    ).with_entities(User.email).all()
    
    if not recipients:
        return
        
    send_email(
        '[Reporte Diario] Estado del Inventario',
        recipients=[email[0] for email in recipients],
        text_body=render_template('email/daily_report.txt',
                                data=report_data),
        html_body=render_template('email/daily_report.html',
                                data=report_data)
    )

def send_transaction_notification(transaction):
    """
    Envía notificación de nueva transacción a los interesados.
    
    Args:
        transaction: Objeto Transacción
    """
    # Obtener destinatarios relevantes (admin, gerente del área, etc.)
    recipients = []
    
    if transaction.customer and transaction.customer.email:
        recipients.append(transaction.customer.email)
    
    if transaction.product.supplier and transaction.product.supplier.email:
        recipients.append(transaction.product.supplier.email)
    
    if recipients:
        send_email(
            f'[Transacción] {transaction.type.title()} de Producto',
            recipients=recipients,
            text_body=render_template('email/transaction_notification.txt',
                                    transaction=transaction),
            html_body=render_template('email/transaction_notification.html',
                                    transaction=transaction)
        )
