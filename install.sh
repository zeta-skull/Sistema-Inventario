#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Iniciando instalación del Sistema de Gestión de Inventario CODEP...${NC}"

# Verificar si se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Por favor, ejecute como root (sudo)${NC}"
    exit 1
fi

# Función para verificar el éxito de los comandos
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 completado${NC}"
    else
        echo -e "${RED}✗ Error en $1${NC}"
        exit 1
    fi
}

# Actualizar sistema
echo -e "${YELLOW}Actualizando sistema...${NC}"
apt update && apt upgrade -y
check_success "Actualización del sistema"

# Instalar dependencias del sistema
echo -e "${YELLOW}Instalando dependencias del sistema...${NC}"
apt install -y python3.9 python3.9-venv python3.9-dev \
    git sqlite3 build-essential libssl-dev libffi-dev
check_success "Instalación de dependencias del sistema"

# Crear directorio de la aplicación si no existe
echo -e "${YELLOW}Configurando directorios...${NC}"
APP_DIR="$PWD"
check_success "Configuración de directorios"

# Crear y activar entorno virtual
echo -e "${YELLOW}Configurando entorno virtual...${NC}"
python3.9 -m venv venv
source venv/bin/activate
check_success "Configuración del entorno virtual"

# Actualizar pip e instalar dependencias
echo -e "${YELLOW}Instalando dependencias Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
check_success "Instalación de dependencias Python"

# Crear directorios necesarios
echo -e "${YELLOW}Creando estructura de directorios...${NC}"
mkdir -p static/uploads
mkdir -p static/product_images
mkdir -p backups
mkdir -p reports
mkdir -p instance
check_success "Creación de estructura de directorios"

# Configurar permisos
echo -e "${YELLOW}Configurando permisos...${NC}"
chmod -R 755 .
chmod -R 770 instance static/uploads static/product_images backups reports
check_success "Configuración de permisos"

# Configurar variables de entorno
echo -e "${YELLOW}Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    cp env.example .env
    echo -e "${YELLOW}Archivo .env creado. Por favor, edítelo con sus configuraciones.${NC}"
fi
check_success "Configuración de variables de entorno"

# Inicializar base de datos
echo -e "${YELLOW}Inicializando base de datos...${NC}"
export FLASK_APP=app.py
flask db upgrade
check_success "Inicialización de base de datos"

# Crear servicio systemd
echo -e "${YELLOW}Configurando servicio systemd...${NC}"
cat > /etc/systemd/system/inventario.service << EOL
[Unit]
Description=Servicio de Gestión de Inventario
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOL
check_success "Configuración del servicio systemd"

# Iniciar y habilitar servicio
echo -e "${YELLOW}Iniciando servicio...${NC}"
systemctl daemon-reload
systemctl start inventario
systemctl enable inventario
check_success "Inicio del servicio"

echo -e "${GREEN}¡Instalación completada!${NC}"
echo -e "${GREEN}Corporacion municipal de desarrollo social de Pudahuel${NC}"
echo -e "${YELLOW}Pasos siguientes:${NC}"
echo "1. Editar el archivo .env con sus configuraciones"
echo "2. Crear un usuario administrador ejecutando:"
echo "   source venv/bin/activate && flask create-admin"
echo "3. Acceder a la aplicación en: http://localhost:5000"
echo -e "${YELLOW}Para ver los logs del servicio:${NC} sudo journalctl -u inventario"
