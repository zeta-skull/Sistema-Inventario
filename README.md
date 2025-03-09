# Sistema de Gestión de Inventario CODEP

Un sistema completo de gestión de inventario construido con Flask, SQLAlchemy y Tailwind CSS. Este sistema proporciona control total sobre su inventario con características como gestión de productos, seguimiento de stock, roles de usuario y notificaciones automatizadas, entre otras opciones.

## Características

- **Autenticación y Autorización de Usuarios**
  - Sistema seguro de inicio de sesión con control de acceso basado en roles
  - Funcionalidad de restablecimiento de contraseña
  - Gestión de perfiles de usuario
  - Múltiples roles de usuario (Administrador, Gerente, Personal)

- **Gestión de Inventario**
  - Operaciones CRUD de productos
  - Gestión de categorías
  - Seguimiento de niveles de stock
  - Carga masiva de productos vía Excel
  - Soporte para carga de imágenes
  - Funcionalidad de búsqueda avanzada

- **Gestión de Proveedores**
  - Operaciones CRUD de proveedores
  - Asociación de proveedores con productos
  - Gestión de información de contacto

- **Gestión de Transacciones**
  - Seguimiento de entradas y salidas de stock
  - Historial de transacciones
  - Asociación con clientes
  - Actualizaciones automáticas de nivel de stock

- **Sistema de Reportes**
  - Generación de reportes en PDF y Excel
  - Reportes de estado de stock
  - Reportes de historial de transacciones
  - Alertas de stock bajo

- **Sistema de Notificaciones**
  - Notificaciones por correo de stock bajo
  - Reportes diarios de inventario
  - Correos de bienvenida para nuevos usuarios
  - Correos de restablecimiento de contraseña

- **Personalización del Sistema**
  - Temas personalizables
  - Gestión de logo de empresa
  - Configuración de ajustes del sistema
  - Gestión de permisos de roles

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tuusuario/sistema-inventario.git
   cd sistema-inventario
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Editar el archivo `.env` con su configuración.

5. Inicializar la base de datos:
   ```bash
   flask db upgrade
   ```

6. Crear directorios requeridos:
   ```bash
   mkdir -p static/uploads static/product_images backups reports
   ```

7. Ejecutar la aplicación:
   ```bash
   flask run
   ```

## Configuración Inicial

1. Crear usuario administrador:
   ```bash
   flask create-admin
   ```

2. Iniciar sesión con las credenciales de administrador:
   - Usuario: admin
   - Contraseña: (la que estableció durante la creación)

3. Configurar ajustes del sistema:
   - Ir a Admin > Ajustes
   - Configurar información de la empresa
   - Configurar ajustes de correo
   - Configurar preferencias de tema

## Uso

### Gestión de Usuarios

- **Agregar Usuarios**: El administrador puede agregar nuevos usuarios a través de Admin > Usuarios > Agregar Usuario
- **Gestionar Roles**: Configurar permisos de roles a través de Admin > Roles
- **Estado de Usuario**: Activar/desactivar usuarios según sea necesario

### Gestión de Inventario

- **Agregar Productos**: 
  1. Ir a Productos > Agregar Producto
  2. Completar detalles del producto
  3. Subir imagen del producto (opcional)
  4. Establecer niveles de stock y alertas

- **Gestión de Stock**:
  1. Registrar movimientos de stock a través de Transacciones
  2. Monitorear niveles de stock a través del Panel
  3. Recibir alertas de stock bajo

### Reportes

- Generar reportes a través de la sección Reportes
- Elegir entre formatos PDF y Excel
- Filtrar por rango de fechas y tipo de reporte

## Desarrollo

### Estructura del Proyecto

```
sistema-inventario/
├── app.py              # Punto de entrada de la aplicación
├── requirements.txt    # Dependencias Python
├── .env               # Variables de entorno
├── models/            # Modelos de base de datos
├── routes/            # Manejadores de rutas
├── forms/             # Definiciones de formularios
├── templates/         # Plantillas HTML
├── static/            # Archivos estáticos
├── utils/             # Funciones utilitarias
└── migrations/        # Migraciones de base de datos
```

### Agregar Nuevas Características

1. Crear modelos de base de datos necesarios en `models/`
2. Agregar formularios en `forms/`
3. Crear rutas en `routes/`
4. Agregar plantillas en `templates/`
5. Actualizar permisos en roles si es necesario

## Seguridad

- Protección contra inyección SQL a través de SQLAlchemy
- Encriptación de contraseñas usando Werkzeug
- Protección CSRF en todos los formularios
- Control de acceso basado en roles
- Validación segura de carga de archivos
- Limitación de tasa en endpoints de autenticación

## Mantenimiento

### Respaldo de Base de Datos

- Respaldos diarios automáticos
- Respaldo manual a través de Admin > Ajustes > Respaldo
- Política de retención de respaldos configurable

### Actualizaciones del Sistema

1. Obtener últimos cambios
2. Instalar nuevas dependencias
3. Ejecutar migraciones de base de datos
4. Reiniciar aplicación

## Solución de Problemas

### Problemas Comunes

1. **Correo no enviado**
   - Verificar configuración SMTP en .env
   - Verificar credenciales de correo
   - Revisar carpeta de spam

2. **Problemas de carga de archivos**
   - Verificar permisos de directorio de carga
   - Revisar límites de tamaño de archivo
   - Verificar tipos de archivo permitidos

3. **Errores de base de datos**
   - Verificar conexión de base de datos
   - Verificar que las migraciones estén actualizadas
   - Revisar espacio en disco


## Licencia

Este proyecto está creado por Eduardo Martinez para el Departamento de informatica de la Corporacion de Pudahuel 2025 ® - Todos los derechos reservados.
