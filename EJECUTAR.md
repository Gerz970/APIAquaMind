# 🚀 Cómo Ejecutar APIAquaMind

## 📋 Requisitos Previos

1. **Python 3.10+** instalado
2. **Dependencias** instaladas: `pip install -r requirements.txt`
3. **Variables de entorno** configuradas (ver `env.example`)

## 🎯 Opciones de Ejecución

### **Opción 1: Script de Inicio Recomendado (Más Fácil)**

```bash
# Desde el directorio raíz del proyecto
python start.py
```

### **Opción 2: Punto de Entrada Principal**

```bash
# Desde el directorio raíz del proyecto
python main.py
```

### **Opción 3: Script con Configuración Automática**

```bash
# Desde el directorio raíz del proyecto
python setup_env.py
```

### **Opción 4: Script Alternativo**

```bash
# Desde el directorio raíz del proyecto
python run.py
```

### **Opción 5: Módulo Python**

```bash
# Desde el directorio raíz del proyecto
python -m app.main
```

## ⚠️ Problemas Comunes y Soluciones

### **Error: "No module named 'app'"**

**Causa**: Estás ejecutando desde el directorio incorrecto o el PYTHONPATH no está configurado.

**Solución**:
```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd C:\GerzApps\aquaMind\APIAquaMind

# Luego ejecuta
python start.py
```

### **Error: "attempted relative import with no known parent package"**

**Causa**: Estás ejecutando `app/main.py` directamente.

**Solución**: Usa uno de los scripts del directorio raíz en lugar de ejecutar `app/main.py` directamente.

### **Error: "ModuleNotFoundError"**

**Causa**: Las dependencias no están instaladas.

**Solución**:
```bash
pip install -r requirements.txt
```

### **Error de Base de Datos**

**Causa**: Variables de entorno no configuradas.

**Solución**:
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tus configuraciones de BD
```

## 🔧 Configuración de Variables de Entorno

1. **Copiar archivo de ejemplo**:
   ```bash
   cp env.example .env
   ```

2. **Editar `.env`** con tus configuraciones:
   ```env
   # Configuración de la aplicación
   FLASK_ENV=development
   DEBUG=True
   PORT=5000
   API_PREFIX=/api/v1

   # Configuración de JWT
   JWT_SECRET_KEY=tu-clave-secreta-aqui
   JWT_ACCESS_TOKEN_EXPIRES=28800

   # Configuración de base de datos SQL Server
   SERVER=tu-servidor
   DATABASE=tu-base-de-datos
   USER=tu-usuario
   PASSWORD=tu-contraseña

   # Configuración de logging
   LOG_LEVEL=INFO
   ```

## 🌐 Acceso a la Aplicación

Una vez ejecutada correctamente, podrás acceder a:

- **API**: http://localhost:5000/api/v1
- **Documentación**: http://localhost:5000/apidocs
- **Health Check**: http://localhost:5000/health

## 🐳 Ejecución con Docker

```bash
# Construir y ejecutar con Docker Compose
docker-compose up --build

# O solo la aplicación
docker build -t apiaquamind .
docker run -p 5000:5000 --env-file .env apiaquamind
```

## 🧪 Ejecución de Tests

```bash
# Ejecutar todos los tests
python -m pytest

# Ejecutar tests específicos
python -m pytest tests/test_jwt_validation.py -v

# Con coverage
python -m pytest --cov=app
```

## 📝 Logs y Debugging

- **Logs**: Se muestran en la consola
- **Debug**: Activado por defecto en desarrollo
- **Errores**: Se muestran con detalles en modo debug

## 🆘 Si Nada Funciona

1. **Verificar Python**: `python --version` (debe ser 3.10+)
2. **Verificar dependencias**: `pip list`
3. **Verificar directorio**: `pwd` o `dir` (debe estar en el directorio raíz)
4. **Verificar archivo .env**: Debe existir y tener las configuraciones correctas
5. **Reinstalar dependencias**: `pip install -r requirements.txt --force-reinstall`

## 📞 Soporte

Si sigues teniendo problemas, verifica:
- La versión de Python
- Las dependencias instaladas
- La configuración de la base de datos
- Los logs de error en la consola 