"""
Módulo principal de la aplicación APIAquaMind.

Este módulo implementa el patrón Application Factory de Flask, que permite:
- Crear múltiples instancias de la aplicación con diferentes configuraciones
- Facilitar el testing con configuraciones específicas
- Mejorar la modularidad y mantenibilidad del código
- Separar la creación de la aplicación de su ejecución

El patrón Factory es especialmente útil para:
- Testing: Crear apps con configuraciones de prueba
- Diferentes entornos: Desarrollo, staging, producción
- Múltiples instancias: Para load balancing o microservicios
"""

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config


def create_app(config_class=Config):
    """
    Función factory para crear la instancia de Flask.
    
    Esta función centraliza toda la configuración de la aplicación:
    1. Crea la instancia de Flask
    2. Aplica la configuración
    3. Inicializa todas las extensiones
    4. Registra los blueprints (rutas)
    5. Configura los manejadores de errores
    
    Args:
        config_class: Clase de configuración a usar (por defecto Config)
        
    Returns:
        Flask app: Instancia configurada de la aplicación Flask
    """
    # Crear la instancia de Flask
    app = Flask(__name__)
    
    # Aplicar la configuración desde la clase especificada
    app.config.from_object(config_class)
    
    # Inicializar todas las extensiones de Flask
    initialize_extensions(app)
    
    # Registrar todos los blueprints (módulos de rutas)
    register_blueprints(app)
    
    # Configurar manejadores de errores personalizados
    register_error_handlers(app)
    
    return app


def initialize_extensions(app):
    """
    Inicializar todas las extensiones de Flask.
    
    Las extensiones son módulos que agregan funcionalidad a Flask:
    - CORS: Permite requests desde otros dominios
    - Swagger: Genera documentación automática de la API
    - JWT: Maneja autenticación con tokens JSON Web
    - Limiter: Protege contra ataques de fuerza bruta
    
    Args:
        app: Instancia de Flask a configurar
    """
    # CORS (Cross-Origin Resource Sharing)
    # Permite que el frontend haga requests a la API desde diferentes dominios
    CORS(app)
    
    # Swagger - Documentación automática de la API
    # Genera una interfaz web en /apidocs para probar los endpoints
    Swagger(app)
    
    # JWT (JSON Web Tokens) - Sistema de autenticación
    # Maneja la creación, validación y renovación de tokens
    jwt = JWTManager(app)
    
    # Rate Limiting - Protección contra ataques
    # Limita el número de requests por IP para prevenir spam/ataques
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,  # Usa la IP del cliente como clave
        default_limits=["200 per day", "100 per hour"]  # Límites por defecto
    )
    
    # Configurar manejadores de errores personalizados para JWT
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        """
        Se ejecuta cuando no se proporciona un token JWT válido.
        Retorna un mensaje de error en español.
        """
        return {
            "error": "Token de autorización no proporcionado o inválido",
            "mensaje": "Por favor, proporciona un token válido para acceder a este recurso."
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """
        Se ejecuta cuando el token JWT es inválido o está malformado.
        """
        return {
            "error": "Token inválido",
            "mensaje": "El token proporcionado no es válido."
        }, 401


def register_blueprints(app):
    """
    Registrar todos los blueprints de la aplicación.
    
    Los blueprints son módulos que contienen rutas relacionadas.
    Esto permite organizar mejor el código y separar funcionalidades.
    
    Args:
        app: Instancia de Flask donde registrar los blueprints
    """
    # Importar los blueprints (se hace aquí para evitar imports circulares)
    from routes.auth.login import auth
    from routes.usuarios.routes_usuario import usuarios
    
    # Registrar cada blueprint con su prefijo de URL
    # API_PREFIX viene de la configuración (ej: /api/v1)
    app.register_blueprint(auth, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(usuarios, url_prefix=app.config['API_PREFIX'])


def register_error_handlers(app):
    """
    Registrar manejadores de errores personalizados.
    
    Estos manejadores capturan errores HTTP específicos y retornan
    respuestas JSON consistentes en lugar de páginas HTML por defecto.
    
    Args:
        app: Instancia de Flask donde registrar los manejadores
    """
    from flask import jsonify
    
    @app.errorhandler(404)
    def handle_404(error):
        """
        Maneja errores 404 - Recurso no encontrado.
        Se ejecuta cuando se accede a una URL que no existe.
        """
        return jsonify({
            "code": 404, 
            "error": "Resource not found",
            "message": "El recurso solicitado no fue encontrado."
        }), 404

    @app.errorhandler(500)
    def handle_500(error):
        """
        Maneja errores 500 - Error interno del servidor.
        Se ejecuta cuando ocurre una excepción no manejada.
        """
        return jsonify({
            "code": 500, 
            "error": "Internal server error",
            "message": "Ocurrió un error interno en el servidor."
        }), 500
    
    @app.errorhandler(400)
    def handle_400(error):
        """
        Maneja errores 400 - Solicitud incorrecta.
        Se ejecuta cuando los datos enviados son inválidos.
        """
        return jsonify({
            "code": 400,
            "error": "Bad request",
            "message": "La solicitud es incorrecta o está mal formada."
        }), 400 