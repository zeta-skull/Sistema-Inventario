# Guía de Instalación del Sistema de Gestión de Inventario

## Requisitos Previos

### 1. Python 3.9
```bash
# En Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# En CentOS/RHEL
sudo yum install python39 python39-devel
```

### 2. Dependencias del Sistema
```bash
# Ubuntu/Debian
sudo apt install git sqlite3 build-essential libssl-dev libffi-dev

# CentOS/RHEL
sudo yum install git sqlite-devel gcc openssl-devel libffi-devel
```

## Pasos de Instalación

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

### 2. Crear y Activar Entorno Virtual
```bash
# Crear entorno virtual
python3.9 -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias Python
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Versiones específicas de las dependencias principales:
- Flask==2.3.3
- Werkzeug==2.3.7
- Flask-SQLAlchemy==3.0.5
- Flask-Login==0.6.2
- Flask-JWT-Extended==4.5.2
- Flask-Mail==0.9.1
- Flask-WTF==1.1.1
- gunicorn==21.2.0

### 4. Configurar Variables de Entorno
1. Copiar el archivo de ejemplo:
```bash
cp env.example .env
```

2. Editar el archivo .env con tus configuraciones:
```
# Configuración de Flask
SECRET_KEY=tu_clave_secreta
FLASK_APP=app.py
FLASK_ENV=production  # Cambiar a 'development' para desarrollo
DEBUG=False          # Cambiar a True para desarrollo

# Base de Datos
DATABASE_URL=sqlite:///inventario.db

# Configuración de Correo (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
```

### 5. Crear Directorios Necesarios
```bash
mkdir -p static/uploads
mkdir -p static/product_images
mkdir -p backups
mkdir -p reports
mkdir -p instance
```

### 6. Inicializar la Base de Datos
```bash
flask db upgrade
```

### 7. Crear Usuario Administrador
```bash
flask create-admin
```

## Ejecución del Sistema

### Desarrollo
```bash
flask run
```

### Producción con Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 4 app:app
```

## Ejecución con Docker

### 1. Construir la Imagen
```bash
docker build -t inventario-app .
```

### 2. Ejecutar con Docker Compose
```bash
docker-compose up -d
```

## Verificación de la Instalación

1. Acceder a la aplicación:
   - Desarrollo: http://localhost:5000
   - Producción: http://tu-dominio:5000

2. Iniciar sesión con las credenciales de administrador creadas

## Solución de Problemas Comunes

### Error de Permisos
```bash
# Corregir permisos de directorios
chmod -R 755 static/uploads
chmod -R 755 instance
```

### Error de Base de Datos
```bash
# Reiniciar la base de datos
rm instance/inventario.db
flask db upgrade
flask create-admin
```

### Error de Dependencias
```bash
# Reinstalar dependencias
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## Mantenimiento

### Respaldos
```bash
# Crear respaldo manual
flask backup-create

# Restaurar respaldo
flask backup-restore <nombre_archivo>
```

### Actualización
```bash
# Actualizar código
git pull origin main

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Actualizar base de datos
flask db upgrade
```

## Notas Importantes

1. **Seguridad**:
   - Cambiar todas las claves secretas en producción
   - Usar contraseñas seguras para la base de datos y el administrador
   - Mantener el modo DEBUG desactivado en producción

2. **Correo Electrónico**:
   - Para Gmail, usar una "Contraseña de aplicación" específica
   - Verificar la configuración del firewall para el puerto SMTP

3. **Base de Datos**:
   - Realizar respaldos regulares
   - Monitorear el espacio en disco
   - Considerar migrar a PostgreSQL para mayor escala

4. **Rendimiento**:
   - Ajustar el número de workers de Gunicorn según los recursos del servidor
   - Monitorear el uso de memoria y CPU
   - Configurar un servidor web (nginx) como proxy inverso en producción
