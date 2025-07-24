# APIAquaMind - Guía de Docker

Esta guía te ayudará a contenerizar y desplegar la aplicación APIAquaMind usando Docker.

## 📋 Prerrequisitos

- Docker instalado en tu sistema
- Docker Compose instalado
- Git para clonar el repositorio

## 🚀 Despliegue Rápido

### 1. Construir y ejecutar con Docker Compose

```bash
# Construir y ejecutar en modo producción
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build

# Ver logs
docker-compose logs -f apiaquamind
```

### 2. Ejecutar solo con Docker

```bash
# Construir la imagen
docker build -t apiaquamind:latest .

# Ejecutar el contenedor
docker run -d \
  --name apiaquamind-api \
  -p 5000:5000 \
  --env-file .env \
  apiaquamind:latest
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Configuración de la aplicación
FLASK_ENV=production
FLASK_APP=app.main
DEBUG=false

# Configuración de base de datos
DATABASE_URL=your_database_connection_string

# Configuración de JWT
JWT_SECRET_KEY=your_jwt_secret_key

# Configuración de seguridad
SECRET_KEY=your_secret_key
```

### Archivo .env.dev para desarrollo

```env
FLASK_ENV=development
FLASK_APP=app.main
DEBUG=true
DATABASE_URL=your_dev_database_connection_string
JWT_SECRET_KEY=dev_jwt_secret_key
SECRET_KEY=dev_secret_key
```

## 🛠️ Comandos Útiles

### Docker Compose

```bash
# Iniciar servicios
docker-compose up

# Iniciar en modo desarrollo
docker-compose --profile dev up

# Iniciar en modo producción con nginx
docker-compose --profile production up

# Detener servicios
docker-compose down

# Reconstruir y reiniciar
docker-compose up --build --force-recreate

# Ver logs de un servicio específico
docker-compose logs -f apiaquamind

# Ejecutar comandos dentro del contenedor
docker-compose exec apiaquamind python -c "print('Hello from container')"
```

### Docker

```bash
# Construir imagen
docker build -t apiaquamind:latest .

# Ejecutar contenedor
docker run -d -p 5000:5000 --name apiaquamind-api apiaquamind:latest

# Ver logs
docker logs -f apiaquamind-api

# Ejecutar comandos interactivos
docker exec -it apiaquamind-api bash

# Detener y eliminar contenedor
docker stop apiaquamind-api && docker rm apiaquamind-api

# Eliminar imagen
docker rmi apiaquamind:latest
```

## 🔍 Monitoreo y Health Checks

La aplicación incluye health checks automáticos:

```bash
# Verificar estado del contenedor
docker ps

# Ver logs de health check
docker logs apiaquamind-api 2>&1 | grep health

# Verificar endpoint de salud manualmente
curl http://localhost:5000/health
```

## 📊 Logs y Debugging

### Ver logs en tiempo real

```bash
# Docker Compose
docker-compose logs -f apiaquamind

# Docker
docker logs -f apiaquamind-api
```

### Acceder al contenedor para debugging

```bash
# Docker Compose
docker-compose exec apiaquamind bash

# Docker
docker exec -it apiaquamind-api bash
```

## 🔒 Seguridad

### Usuario no-root

La aplicación se ejecuta con un usuario no-root (`appuser`) para mayor seguridad.

### Variables de entorno sensibles

- Nunca incluyas credenciales en el Dockerfile
- Usa archivos `.env` para variables sensibles
- Considera usar Docker Secrets para producción

### Escaneo de vulnerabilidades

```bash
# Escanear imagen en busca de vulnerabilidades
docker scan apiaquamind:latest
```

## 🚀 Despliegue en Producción

### 1. Configuración de producción

```bash
# Crear archivo .env.production
cp .env .env.production
# Editar variables para producción
```

### 2. Desplegar con Docker Compose

```bash
# Desplegar con nginx
docker-compose --profile production up -d

# Verificar servicios
docker-compose ps
```

### 3. Configuración de nginx (opcional)

Si usas nginx como reverse proxy, crea un archivo `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream apiaquamind {
        server apiaquamind:5000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://apiaquamind;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 🧹 Limpieza

### Limpiar recursos Docker

```bash
# Eliminar contenedores detenidos
docker container prune

# Eliminar imágenes no utilizadas
docker image prune

# Eliminar volúmenes no utilizados
docker volume prune

# Limpieza completa (¡cuidado!)
docker system prune -a
```

### Limpiar logs

```bash
# Limpiar logs del contenedor
docker logs --since 0 apiaquamind-api > /dev/null

# Limpiar logs de Docker Compose
docker-compose logs --since 0 > /dev/null
```

## 📝 Troubleshooting

### Problemas comunes

1. **Puerto ya en uso**
   ```bash
   # Cambiar puerto en docker-compose.yml
   ports:
     - "5001:5000"  # Usar puerto 5001 en lugar de 5000
   ```

2. **Error de permisos**
   ```bash
   # Verificar permisos del directorio
   ls -la
   # Ajustar permisos si es necesario
   chmod 755 .
   ```

3. **Problemas de conectividad de base de datos**
   ```bash
   # Verificar variables de entorno
   docker-compose exec apiaquamind env | grep DATABASE
   ```

4. **Imagen no se construye**
   ```bash
   # Limpiar caché de Docker
   docker builder prune
   # Reconstruir sin caché
   docker build --no-cache -t apiaquamind:latest .
   ```

## 📚 Recursos Adicionales

- [Documentación oficial de Docker](https://docs.docker.com/)
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Flask Docker deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/docker/)
- [Python Docker best practices](https://docs.docker.com/language/python/)

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz tus cambios
4. Prueba con Docker
5. Envía un pull request

---

**Nota**: Asegúrate de que tu archivo `.env` esté configurado correctamente antes de ejecutar los contenedores. 