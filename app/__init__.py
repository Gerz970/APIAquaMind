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
    
    # Inicializar cliente MQTT
    initialize_mqtt_client(app)
    
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


def initialize_mqtt_client(app):
    """
    Inicializar cliente MQTT para HiveMQ Cloud.
    
    Args:
        app: Instancia de Flask donde configurar el cliente MQTT
    """
    # Verificar si MQTT está habilitado
    if not app.config.get('MQTT_ENABLED', True):
        app.logger.info("MQTT está deshabilitado por configuración. No se inicializará el cliente MQTT.")
        app.mqtt_client = None
        app.mqtt_message_handler = None
        app.device_monitor = None
        return
    
    try:
        from services.mqtt_client import HiveMQClient
        from services.mqtt_message_handler import MQTTMessageHandler
        from core.device_monitor import DeviceMonitor
        
        # Crear cliente MQTT
        mqtt_client = HiveMQClient(app.config)
        
        # Configurar manejador de mensajes
        message_handler = MQTTMessageHandler()
        mqtt_client.message_handler = message_handler
        
        # Crear monitor de dispositivos
        device_monitor = DeviceMonitor(mqtt_client)
        
        # Iniciar cliente en un hilo separado
        import threading
        mqtt_thread = threading.Thread(target=mqtt_client.start, daemon=True)
        mqtt_thread.start()
        
        # Iniciar monitoreo de dispositivos
        device_monitor.start_monitoring()
        
        # Guardar en app para acceso global
        app.mqtt_client = mqtt_client
        app.mqtt_message_handler = message_handler
        app.device_monitor = device_monitor
        
        app.logger.info("Cliente MQTT y monitor de dispositivos inicializados exitosamente")
        
    except Exception as e:
        app.logger.error(f"Error inicializando cliente MQTT: {e}")
        app.mqtt_client = None
        app.mqtt_message_handler = None
        app.device_monitor = None
        
        # Iniciar generación de datos dummy cuando MQTT está apagado
        app.logger.info("MQTT no disponible - Iniciando generación de datos dummy")
        start_dummy_data_generation(app)


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
    from routes.routes_usuario import usuarios
    from routes.routes_nodos import nodos
    from routes.routes_eventos import eventos
    from routes.routes_recomendaciones import recomendaciones
    from routes.routes_mqtt import mqtt_control
    from routes.routes_notificaciones import notificaciones
    from routes.routes_configuraciones import configuraciones
    from routes.routes_niveles_agua import niveles_agua
    
    # Registrar cada blueprint con su prefijo de URL
    # API_PREFIX viene de la configuración (ej: /api/v1)
    app.register_blueprint(auth, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(usuarios, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(nodos, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(eventos, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(recomendaciones, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(mqtt_control, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(notificaciones, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(configuraciones, url_prefix=app.config['API_PREFIX'])
    app.register_blueprint(niveles_agua, url_prefix=app.config['API_PREFIX'])

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


def start_dummy_data_generation(app):
    """
    Iniciar generación automática de datos dummy cuando MQTT está apagado.
    
    Args:
        app: Instancia de Flask
    """
    import threading
    import time
    from datetime import datetime
    from core.mqtt_data_processor import MQTTDataProcessor
    
    def generate_dummy_data_loop():
        """
        Loop que genera datos dummy cada 30 segundos.
        """
        data_processor = MQTTDataProcessor()
        
        while True:
            try:
                # Verificar si MQTT sigue apagado
                if hasattr(app, 'mqtt_client') and app.mqtt_client:
                    app.logger.info("MQTT disponible - Deteniendo generación de datos dummy")
                    break
                
                # Generar y procesar datos dummy
                app.logger.info("Generando datos dummy del nivel de agua...")
                success = data_processor.process_dummy_water_level_data()
                
                if success:
                    app.logger.info("Datos dummy procesados exitosamente")
                else:
                    app.logger.warning("Error procesando datos dummy")
                
                # Esperar 30 segundos antes de la siguiente generación
                time.sleep(30)
                
            except Exception as e:
                app.logger.error(f"Error en loop de datos dummy: {e}")
                time.sleep(30)  # Esperar antes de reintentar
    
    # Iniciar el loop en un hilo separado
    dummy_thread = threading.Thread(target=generate_dummy_data_loop, daemon=True)
    dummy_thread.start()
    
    app.logger.info("Generación automática de datos dummy iniciada") 