# 🗄️ Configuración de Base de Datos APIAquaMind

## 📋 Requisitos Previos

1. **SQL Server** instalado y funcionando
2. **ODBC Driver 17 for SQL Server** instalado
3. **Credenciales** de acceso a la base de datos
4. **Permisos** para crear tablas y usuarios

## 🔧 Paso 1: Configurar Variables de Entorno

### **Para Desarrollo (Recomendado para empezar):**

```bash
# Copiar archivo de ejemplo
copy env.example .env
```

Editar `.env` con tus datos reales:

```env
# Configuración de la aplicación
FLASK_ENV=development
DEBUG=True
PORT=5000
API_PREFIX=/api/v1

# Configuración de JWT
JWT_SECRET_KEY=mi-clave-secreta-para-desarrollo
JWT_ACCESS_TOKEN_EXPIRES=28800

# Configuración de base de datos SQL Server REAL
SERVER=tu-servidor-sql-server.com
DATABASE=tu-base-de-datos-real
USER=tu-usuario-de-bd
PASSWORD=tu-contraseña-de-bd

# Configuración de logging
LOG_LEVEL=INFO
```

### **Para Producción:**

```bash
# Copiar archivo de producción
copy env.production .env
```

Editar `.env` con datos de producción:

```env
# Configuración de la aplicación
FLASK_ENV=production
DEBUG=False
PORT=5000
API_PREFIX=/api/v1

# Configuración de JWT (CAMBIAR POR UNA CLAVE REAL)
JWT_SECRET_KEY=clave-super-secreta-para-produccion-cambiar-por-una-real
JWT_ACCESS_TOKEN_EXPIRES=28800

# Configuración de base de datos SQL Server REAL
SERVER=servidor-produccion.com
DATABASE=base-datos-produccion
USER=usuario-produccion
PASSWORD=contraseña-produccion

# Configuración de logging para producción
LOG_LEVEL=WARNING
```

## 🔍 Paso 2: Verificar Conexión a Base de Datos

### **Opción A: Script Automático (Recomendado)**

```bash
# Ejecutar script de configuración
python scripts/setup_database.py
```

Este script:
- ✅ Verifica la conexión
- ✅ Crea las tablas necesarias
- ✅ Inserta datos de prueba
- ✅ Valida la configuración

### **Opción B: Verificación Manual**

```bash
# Ejecutar la aplicación
python start.py
```

Si no hay errores de conexión, la configuración es correcta.

## 🏗️ Paso 3: Estructura de Base de Datos

### **Tabla Principal: tb_usuario**

```sql
CREATE TABLE tb_usuario (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(25) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    correo_electronico VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NULL DEFAULT '',
    fecha_nacimiento DATETIME NULL,
    id_tipo_usuario INT NOT NULL DEFAULT 1,
    id_estatus INT NOT NULL DEFAULT 1,
    fecha_registro DATETIME NOT NULL DEFAULT GETDATE()
);
```

### **Datos de Prueba Creados Automáticamente:**

- **Usuario**: `admin`
- **Contraseña**: `Admin123!`
- **Email**: `admin@aquamind.com`

## 🚀 Paso 4: Ejecutar la Aplicación

### **Modo Desarrollo:**
```bash
python start.py
```

### **Modo Producción:**
```bash
python scripts/load_production.py
```

## 🧪 Paso 5: Probar la Conexión

### **1. Probar Login:**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "user": "admin",
    "password": "Admin123!"
  }'
```

### **2. Probar Validación JWT:**
```bash
# Primero obtener token del login anterior
curl -X POST http://localhost:5000/api/v1/auth/validate \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TU_TOKEN_AQUI"
  }'
```

### **3. Acceder a Documentación:**
- **URL**: http://localhost:5000/apidocs
- **Descripción**: Interfaz Swagger para probar endpoints

## ⚠️ Problemas Comunes y Soluciones

### **Error: "Login failed for user"**

**Causa**: Credenciales incorrectas o usuario sin permisos.

**Solución**:
```sql
-- Verificar que el usuario existe
SELECT * FROM tb_usuario WHERE username = 'admin';

-- Crear usuario manualmente si no existe
INSERT INTO tb_usuario (username, password, correo_electronico, nombre, apellido_paterno)
VALUES ('admin', 'hashed_password', 'admin@aquamind.com', 'Admin', 'Sistema');
```

### **Error: "Cannot connect to server"**

**Causa**: Servidor SQL Server no accesible.

**Solución**:
1. Verificar que SQL Server esté ejecutándose
2. Verificar firewall
3. Verificar configuración de red
4. Probar conexión con SQL Server Management Studio

### **Error: "ODBC Driver not found"**

**Causa**: Driver ODBC no instalado.

**Solución**:
```bash
# Windows: Descargar e instalar ODBC Driver 17 for SQL Server
# Linux: sudo apt-get install unixodbc unixodbc-dev
# Mac: brew install unixodbc
```

### **Error: "Database does not exist"**

**Causa**: Base de datos no creada.

**Solución**:
```sql
-- Crear base de datos
CREATE DATABASE tu_base_de_datos;
GO
USE tu_base_de_datos;
GO
```

## 🔒 Configuración de Seguridad

### **1. Usuario de Base de Datos:**
```sql
-- Crear usuario específico para la aplicación
CREATE LOGIN app_user WITH PASSWORD = 'contraseña-segura';
CREATE USER app_user FOR LOGIN app_user;

-- Asignar permisos mínimos necesarios
GRANT SELECT, INSERT, UPDATE, DELETE ON tb_usuario TO app_user;
```

### **2. Configuración de Red:**
- Usar conexiones encriptadas
- Configurar firewall para permitir solo conexiones necesarias
- Usar puertos no estándar si es posible

### **3. Variables de Entorno:**
- Nunca commitear archivos `.env` con credenciales reales
- Usar variables de entorno del sistema en producción
- Rotar contraseñas regularmente

## 📊 Monitoreo y Logs

### **Verificar Logs de Conexión:**
```bash
# Los logs se muestran en la consola
# Buscar mensajes como:
# "Motor de base de datos inicializado correctamente"
# "Conexión a la base de datos exitosa"
```

### **Verificar Estado de la Base de Datos:**
```sql
-- Verificar conexiones activas
SELECT * FROM sys.dm_exec_sessions WHERE database_id = DB_ID('tu_base_de_datos');

-- Verificar uso de recursos
SELECT * FROM sys.dm_exec_requests WHERE database_id = DB_ID('tu_base_de_datos');
```

## 🎯 Próximos Pasos

1. ✅ Configurar variables de entorno
2. ✅ Verificar conexión a base de datos
3. ✅ Crear tablas y datos de prueba
4. ✅ Probar endpoints de autenticación
5. 🔄 Configurar usuarios reales
6. 🔄 Implementar lógica de negocio adicional
7. 🔄 Configurar monitoreo y alertas
8. 🔄 Preparar para despliegue en producción

## 📞 Soporte

Si tienes problemas:
1. Verifica los logs de la aplicación
2. Verifica la configuración de SQL Server
3. Prueba la conexión manualmente
4. Revisa los errores específicos en la consola 