# Dockerfile para APIAquaMind API
# Usando multi-stage build para optimizar el tamaño de la imagen

# ===========================================
# STAGE 1: Build stage - Instalar dependencias
# ===========================================
FROM python:3.11-slim-bullseye AS builder

# Establecer variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para pyodbc y otras librerías
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app
# Agregar el directorio interno al PYTHONPATH
ENV PYTHONPATH=/app/app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --user -r requirements.txt

# ===========================================
# STAGE 2: Runtime stage - Imagen final
# ===========================================
FROM python:3.11-slim-bullseye

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5000

# Instalar dependencias del sistema para runtime
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc unixodbc-dev gcc g++ libssl-dev libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de trabajo
WORKDIR /app
ENV PYTHONPATH=/app/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/config.py .   
COPY app/ ./app/

# Crear directorio para logs y dar permisos
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Cambiar al usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando para ejecutar la aplicación
CMD ["python", "-m", "app.main"]
