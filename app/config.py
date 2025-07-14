"""
Módulo de configuración para APIAquaMind.

Este módulo maneja toda la configuración de la aplicación usando variables
de entorno. Implementa diferentes configuraciones para diferentes entornos:
- Desarrollo: Configuración para desarrollo local
- Producción: Configuración optimizada para producción
- Testing: Configuración específica para tests

Características:
- Carga automática de variables de entorno
- Validación de configuraciones requeridas
- Configuraciones específicas por entorno
- Valores por defecto seguros
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Cargar variables de entorno desde el archivo .env
# Esto permite tener configuraciones locales sin afectar el repositorio
load_dotenv()

class BaseConfig:
    """
    Configuración base de la aplicación.
    
    Esta clase contiene todas las configuraciones comunes que se aplican
    a todos los entornos (desarrollo, producción, testing).
    
    Las configuraciones se obtienen de variables de entorno con valores
    por defecto seguros para desarrollo.
    """
    
    # Configuración general de la aplicación
    DEBUG = False                    # Modo debug desactivado por defecto
    TESTING = False                  # Modo testing desactivado por defecto
    
    # Configuración de la API
    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")  # Prefijo de todas las rutas
    PORT = int(os.getenv("PORT", 5000))              # Puerto del servidor
    
    # Configuración de JWT (JSON Web Tokens)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")     # Clave secreta para firmar tokens
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 28800))  # 8 horas en segundos
    
    # Configuración de base de datos SQL Server
    SERVER = os.getenv("SERVER")                     # Servidor de BD
    DATABASE = os.getenv("DATABASE")                 # Nombre de la BD
    USER = os.getenv("USER")                         # Usuario de BD
    PASSWORD = os.getenv("PASSWORD")                 # Contraseña de BD
    
    # Configuración de rate limiting (protección contra ataques)
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")       # Nivel de logging
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate_config(cls) -> list:
        """
        Validar que todas las configuraciones requeridas estén presentes.
        
        Este método verifica que las configuraciones críticas para el
        funcionamiento de la aplicación estén definidas.
        
        Returns:
            list: Lista de errores encontrados (vacía si todo está bien)
            
        Example:
            errors = BaseConfig.validate_config()
            if errors:
                for error in errors:
                    print(f"Error de configuración: {error}")
        """
        errors = []
        
        # Lista de configuraciones que son obligatorias
        required_configs = [
            ('JWT_SECRET_KEY', cls.JWT_SECRET_KEY),  # Necesario para firmar tokens
            ('SERVER', cls.SERVER),                   # Servidor de BD
            ('DATABASE', cls.DATABASE),               # Nombre de BD
            ('USER', cls.USER),                       # Usuario de BD
            ('PASSWORD', cls.PASSWORD)                # Contraseña de BD
        ]
        
        # Verificar cada configuración requerida
        for config_name, config_value in required_configs:
            if not config_value:
                errors.append(f"Configuración requerida '{config_name}' no está establecida.")
        
        return errors

class DevelopmentConfig(BaseConfig):
    """
    Configuración para desarrollo.
    
    Esta configuración se usa cuando la aplicación está en modo desarrollo.
    Incluye configuraciones que facilitan el desarrollo como debug activado
    y logging detallado.
    """
    DEBUG = True                     # Activar modo debug para desarrollo
    LOG_LEVEL = "DEBUG"              # Logging detallado para desarrollo

class ProductionConfig(BaseConfig):
    """
    Configuración para producción.
    
    Esta configuración se usa cuando la aplicación está en producción.
    Incluye configuraciones optimizadas para rendimiento y seguridad.
    """
    DEBUG = False                    # Desactivar debug en producción
    LOG_LEVEL = "WARNING"            # Solo warnings y errores en producción

class TestingConfig(BaseConfig):
    """
    Configuración para testing.
    
    Esta configuración se usa cuando se ejecutan tests automatizados.
    Incluye configuraciones específicas para testing como una BD separada.
    """
    TESTING = True                   # Activar modo testing
    DEBUG = True                     # Debug activado para tests
    # Usar base de datos de prueba separada
    DATABASE = os.getenv("TEST_DATABASE", "test_db")

# Configuración por defecto
class Config(BaseConfig):
    """
    Configuración por defecto que se adapta al entorno.
    
    Esta clase hereda de BaseConfig y proporciona métodos para obtener
    la configuración apropiada según el entorno actual.
    """
    
    @classmethod
    def get_config(cls):
        """
        Obtener la configuración apropiada según el entorno.
        
        Este método determina qué configuración usar basándose en la
        variable de entorno FLASK_ENV.
        
        Returns:
            class: Clase de configuración apropiada para el entorno
            
        Example:
            config_class = Config.get_config()
            app.config.from_object(config_class)
        """
        # Obtener el entorno desde variables de entorno
        env = os.getenv("FLASK_ENV", "development").lower()
        
        # Retornar la configuración apropiada según el entorno
        if env == "production":
            return ProductionConfig
        elif env == "testing":
            return TestingConfig
        else:
            return DevelopmentConfig
    
    # Heredar todas las configuraciones de BaseConfig
    # Esto permite usar Config directamente como configuración por defecto
    DEBUG = BaseConfig.DEBUG
    TESTING = BaseConfig.TESTING
    API_PREFIX = BaseConfig.API_PREFIX
    PORT = BaseConfig.PORT
    JWT_SECRET_KEY = BaseConfig.JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = BaseConfig.JWT_ACCESS_TOKEN_EXPIRES
    SERVER = BaseConfig.SERVER
    DATABASE = BaseConfig.DATABASE
    USER = BaseConfig.USER
    PASSWORD = BaseConfig.PASSWORD
    RATELIMIT_DEFAULT = BaseConfig.RATELIMIT_DEFAULT
    RATELIMIT_STORAGE_URL = BaseConfig.RATELIMIT_STORAGE_URL
    LOG_LEVEL = BaseConfig.LOG_LEVEL
    LOG_FORMAT = BaseConfig.LOG_FORMAT
