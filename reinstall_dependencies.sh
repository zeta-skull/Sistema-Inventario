#!/bin/bash

echo "Desactivando entorno virtual actual..."
deactivate 2>/dev/null || true

echo "Eliminando entorno virtual anterior..."
rm -rf venv

echo "Creando nuevo entorno virtual..."
python3.9 -m venv venv

echo "Activando nuevo entorno virtual..."
source venv/bin/activate

echo "Actualizando pip..."
pip install --upgrade pip

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Inicializando la base de datos..."
export FLASK_APP=app.py
flask db init
flask db migrate -m "initial migration"
flask db upgrade

echo "Instalación completada."