import schedule
import time
from datetime import datetime, timedelta
from app import app, db
from models.inventory import Product, Transaction
from models.user import User, Role
from utils.email import send_daily_report
from utils.reports import generate_pdf_report, generate_excel_report
import os
import logging

# Configuración de registro
logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def enviar_reporte_diario_inventario():
    """Genera y envía el reporte diario de inventario"""
    try:
        with app.app_context():
            # Obtener rango de fecha de hoy
            hoy = datetime.now().date()
            fecha_inicio = datetime.combine(hoy, datetime.min.time())
            fecha_fin = datetime.combine(hoy, datetime.max.time())

            # Recopilar datos del reporte
            datos = {
                'fecha': hoy.strftime('%Y-%m-%d'),
                'resumen': {
                    'total_productos': Product.query.count(),
                    'productos_stock_bajo': Product.query.filter(
                        Product.current_stock <= Product.minimum_stock
                    ).count(),
                    'transacciones_diarias': Transaction.query.filter(
                        Transaction.transaction_date.between(fecha_inicio, fecha_fin)
                    ).count()
                },
                'productos_stock_bajo': [
                    {
                        'nombre': p.name,
                        'stock_actual': p.current_stock,
                        'stock_minimo': p.minimum_stock
                    }
                    for p in Product.query.filter(
                        Product.current_stock <= Product.minimum_stock
                    ).all()
                ],
                'transacciones': [
                    {
                        'nombre_producto': t.product.name,
                        'tipo': t.type,
                        'cantidad': t.quantity,
                        'precio_total': t.total_price
                    }
                    for t in Transaction.query.filter(
                        Transaction.transaction_date.between(fecha_inicio, fecha_fin)
                    ).all()
                ]
            }

            # Generar y guardar reportes
            reporte_pdf = generate_pdf_report('inventory', fecha_inicio, fecha_fin)
            reporte_excel = generate_excel_report('inventory', fecha_inicio, fecha_fin)

            # Enviar reporte por correo
            send_daily_report(datos)

            logger.info('Reporte diario de inventario enviado exitosamente')

    except Exception as e:
        logger.error(f'Error al enviar reporte diario de inventario: {str(e)}')

def respaldar_base_datos():
    """Crear respaldo diario de la base de datos"""
    try:
        with app.app_context():
            # Crear directorio de respaldos si no existe
            directorio_respaldo = os.getenv('BACKUP_FOLDER', 'backups')
            os.makedirs(directorio_respaldo, exist_ok=True)

            # Generar nombre de archivo con marca de tiempo
            marca_tiempo = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_respaldo = f'inventario_respaldo_{marca_tiempo}.sql'
            ruta_respaldo = os.path.join(directorio_respaldo, archivo_respaldo)

            # Ejecutar comando de respaldo
            os.system(f'sqlite3 instance/inventory.db .dump > {ruta_respaldo}')

            # Limpiar respaldos antiguos
            dias_retencion = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
            limpiar_respaldos_antiguos(directorio_respaldo, dias_retencion)

            logger.info(f'Respaldo de base de datos creado: {archivo_respaldo}')

    except Exception as e:
        logger.error(f'Error al crear respaldo de base de datos: {str(e)}')

def limpiar_archivos_antiguos():
    """Limpiar reportes y archivos temporales antiguos"""
    try:
        with app.app_context():
            # Limpiar reportes antiguos
            limpiar_directorio('reports', 7)
            
            # Limpiar archivos de carga antiguos
            limpiar_directorio('static/uploads', 30)

            logger.info('Limpieza de archivos completada exitosamente')

    except Exception as e:
        logger.error(f'Error durante la limpieza de archivos: {str(e)}')

def limpiar_directorio(directorio, dias):
    """
    Limpiar archivos en un directorio más antiguos que los días especificados.
    
    Args:
        directorio: Ruta del directorio a limpiar
        dias: Número de días para mantener los archivos
    """
    if not os.path.exists(directorio):
        return

    fecha_limite = datetime.now() - timedelta(days=dias)
    
    for nombre_archivo in os.listdir(directorio):
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        if os.path.isfile(ruta_archivo):
            fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_archivo))
            if fecha_modificacion < fecha_limite:
                os.remove(ruta_archivo)

def limpiar_respaldos_antiguos(directorio_respaldo, dias_retencion):
    """
    Limpiar archivos de respaldo más antiguos que el período de retención.
    
    Args:
        directorio_respaldo: Ruta del directorio de respaldos
        dias_retencion: Número de días para mantener los respaldos
    """
    if not os.path.exists(directorio_respaldo):
        return

    fecha_limite = datetime.now() - timedelta(days=dias_retencion)
    
    for nombre_archivo in os.listdir(directorio_respaldo):
        if nombre_archivo.startswith('inventario_respaldo_') and nombre_archivo.endswith('.sql'):
            ruta_archivo = os.path.join(directorio_respaldo, nombre_archivo)
            fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_archivo))
            if fecha_modificacion < fecha_limite:
                os.remove(ruta_archivo)

def main():
    """Configurar y ejecutar tareas programadas"""
    # Programar reporte diario de inventario (todos los días a las 6:00 AM)
    schedule.every().day.at("06:00").do(enviar_reporte_diario_inventario)

    # Programar respaldo de base de datos (todos los días a la 1:00 AM)
    schedule.every().day.at("01:00").do(respaldar_base_datos)

    # Programar limpieza de archivos (todos los domingos a las 2:00 AM)
    schedule.every().sunday.at("02:00").do(limpiar_archivos_antiguos)

    logger.info('Programador iniciado')

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Esperar un minuto antes de verificar nuevamente
        except Exception as e:
            logger.error(f'Error en el bucle principal del programador: {str(e)}')
            time.sleep(300)  # Esperar 5 minutos antes de reintentar en caso de error

if __name__ == '__main__':
    main()
