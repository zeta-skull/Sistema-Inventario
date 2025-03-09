#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Iniciando despliegue con Docker...${NC}"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker no está instalado. Instalando...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose no está instalado. Instalando...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Crear directorios necesarios
echo -e "${YELLOW}Creando directorios necesarios...${NC}"
mkdir -p static/uploads static/product_images backups reports instance

# Configurar permisos
echo -e "${YELLOW}Configurando permisos...${NC}"
chmod -R 755 .
chmod -R 770 instance static/uploads static/product_images backups reports

# Configurar variables de entorno
echo -e "${YELLOW}Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    cp env.example .env
    echo -e "${YELLOW}Archivo .env creado. Por favor, edítelo con sus configuraciones.${NC}"
fi

# Construir y levantar contenedores
echo -e "${YELLOW}Construyendo y levantando contenedores...${NC}"
docker-compose build
docker-compose up -d

# Verificar estado de los contenedores
echo -e "${YELLOW}Verificando estado de los contenedores...${NC}"
docker-compose ps

echo -e "${GREEN}¡Despliegue completado!${NC}"
echo -e "${YELLOW}Pasos siguientes:${NC}"
echo "1. Editar el archivo .env con sus configuraciones"
echo "2. Crear un usuario administrador ejecutando:"
echo "   docker-compose exec web flask create-admin"
echo "3. Acceder a la aplicación en: http://localhost:5000"
echo -e "${YELLOW}Para ver los logs:${NC} docker-compose logs -f"
echo -e "${YELLOW}Para detener los contenedores:${NC} docker-compose down"
