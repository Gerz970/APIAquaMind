# APIAquaMind

API RESTful desarrollada en Flask para el sistema AquaMind, siguiendo las mejores prácticas de desarrollo y arquitectura escalable.

## 🚀 Características

- **Arquitectura Modular**: Patrón Factory para la aplicación Flask
- **Autenticación JWT**: Sistema de autenticación seguro con tokens
- **Base de Datos SQL Server**: Integración con SQL Server usando SQLAlchemy
- **Validaciones Robustas**: Validación de datos de entrada con mensajes personalizados
- **Rate Limiting**: Protección contra ataques de fuerza bruta
- **Documentación API**: Swagger/OpenAPI integrado
- **Docker**: Containerización completa con Docker y Docker Compose
- **Logging**: Sistema de logging configurable
- **CORS**: Soporte para Cross-Origin Resource Sharing

## 📋 Requisitos Previos

- Python 3.10+
- Docker y Docker Compose
- SQL Server (local o remoto)
- ODBC Driver 17 for SQL Server

## 🛠️ Instalación

### Opción 1: Desarrollo Local

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd APIAquaMind
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app/main.py
   ```

### Opción 2: Docker

1. **Configurar variables de entorno**
   ```bash
   cp env.example .env
   # Editar .env con tus configuraciones
   ```

2. **Ejecutar con Docker Compose**
   ```bash
   docker-compose up --build
   ```

## 🔧 Configuración

### Variables de Entorno

Copia `env.example` a `.env` y configura las siguientes variables:

```env
# Configuración de la aplicación
FLASK_ENV=development
DEBUG=True
PORT=5000
API_PREFIX=/api/v1

# Configuración de JWT
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ACCESS_TOKEN_EXPIRES=28800

# Configuración de base de datos SQL Server
SERVER=your-server-name
DATABASE=your-database-name
USER=your-username
PASSWORD=your-password

# Configuración de rate limiting
RATELIMIT_DEFAULT=200 per day;50 per hour
LOG_LEVEL=INFO
```

## 📚 Estructura del Proyecto

```
APIAquaMind/
├── app/
│   ├── __init__.py              # Application factory
│   ├── main.py                  # Punto de entrada
│   ├── config.py                # Configuraciones
│   ├── core/                    # Lógica de negocio
│   │   ├── auth.py
│   │   └── usuarios.py
│   ├── database/                # Gestión de base de datos
│   │   └── __init__.py
│   ├── models/                  # Modelos SQLAlchemy
│   │   └── seguridad.py
│   ├── routes/                  # Rutas de la API
│   │   ├── auth/
│   │   │   └── login.py
│   │   └── usuarios/
│   │       └── routes_usuario.py
│   ├── services/                # Servicios de aplicación
│   │   ├── __init__.py
│   │   └── auth_service.py
│   └── utils/                   # Utilidades
│       ├── __init__.py
│       ├── connectiondb.py
│       └── validators.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔌 Endpoints de la API

### Autenticación

- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/me` - Obtener usuario actual
- `POST /api/v1/auth/refresh` - Refrescar token

### Usuarios

- `GET /api/v1/usuarios/listar` - Listar usuarios
- `POST /api/v1/usuarios/usuario` - Crear usuario

## 🔒 Seguridad

- **Autenticación JWT**: Tokens de acceso con expiración
- **Encriptación de Contraseñas**: Bcrypt para hashing seguro
- **Rate Limiting**: Protección contra ataques de fuerza bruta
- **Validación de Entrada**: Validación robusta de datos
- **CORS**: Configuración segura para cross-origin requests

## 🧪 Testing

```bash
# Ejecutar tests
python -m pytest

# Con coverage
python -m pytest --cov=app
```

## 📊 Monitoreo y Logging

La aplicación incluye logging configurable con diferentes niveles:

- **DEBUG**: Información detallada para desarrollo
- **INFO**: Información general de la aplicación
- **WARNING**: Advertencias
- **ERROR**: Errores que requieren atención

## 🚀 Despliegue

### Producción con Docker

```bash
# Construir imagen de producción
docker build -t apiaquamind:latest .

# Ejecutar en producción
docker run -d \
  --name apiaquamind \
  -p 5000:5000 \
  --env-file .env \
  apiaquamind:latest
```

### Variables de Entorno para Producción

```env
FLASK_ENV=production
DEBUG=False
JWT_SECRET_KEY=your-production-secret-key
LOG_LEVEL=WARNING
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas, contacta al equipo de desarrollo o crea un issue en el repositorio.