"""
Módulo de rutas de autenticación para APIAquaMind.

Este módulo contiene todas las rutas relacionadas con la autenticación:
- Login de usuarios
- Obtención de información del usuario actual
- Renovación de tokens JWT

Características:
- Rate limiting para prevenir ataques de fuerza bruta
- Validación de datos de entrada
- Manejo de errores consistente
- Documentación automática con Swagger
- Logging detallado de operaciones
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.auth_service import AuthService
from utils.validators import LoginValidator
import logging
from flask import current_app

# Configurar logger específico para rutas de autenticación
logger = logging.getLogger(__name__)

# Blueprint para rutas de autenticación
# Los blueprints permiten organizar rutas relacionadas en módulos separados
auth = Blueprint('auth', __name__)

# Crear instancia de Limiter
limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["100 per hour"]
)

@auth.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Limitar a 5 intentos por minuto por IP
def login():
    """
    Endpoint para autenticación de usuarios (login).
    
    Este endpoint permite a los usuarios autenticarse en el sistema
    proporcionando su username y contraseña. Si las credenciales son
    válidas, retorna un token JWT que debe usarse para acceder a
    otros endpoints protegidos.
    
    Proceso:
    1. Validar datos de entrada
    2. Autenticar usuario con el servicio
    3. Generar token JWT si es exitoso
    4. Retornar token e información del usuario
    
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            user:
              type: string
              description: Nombre de usuario
              example: "usuario123"
            password:
              type: string
              description: Contraseña del usuario
              example: "MiContraseña123"
    responses:
      200:
        description: Login exitoso, se devuelve el token de acceso
        schema:
          type: object
          properties:
            token:
              type: string
              description: Token JWT para autenticación
            type:
              type: string
              description: Tipo de token (siempre "Bearer")
            user:
              type: object
              description: Información del usuario autenticado
      400:
        description: Datos de entrada inválidos o faltantes
      401:
        description: Credenciales inválidas
      429:
        description: Demasiadas solicitudes (rate limit excedido)
      500:
        description: Error interno del servidor
    """
    try:
        # Obtener datos JSON del request
        data = request.get_json()
        
        # Validar que los datos de entrada sean correctos
        validation_errors = LoginValidator.validate_login_data(data)
        if validation_errors:
            return jsonify({
                "error": "Datos de entrada inválidos",
                "details": validation_errors
            }), 400
        
        # Extraer credenciales del request
        user = data.get("username")
        password = data.get("password")
        
        # Autenticar usuario usando el servicio de autenticación
        auth_result = AuthService.authenticate_user(user, password)
        
        # Si la autenticación falla, retornar error 401
        if not auth_result:
            return jsonify({
                "error": "Credenciales inválidas",
                "message": "El usuario o contraseña son incorrectos"
            }), 401
        
        # Log de login exitoso (sin información sensible)
        logger.info(f"Login exitoso para el usuario: {user}")
        
        # Retornar respuesta exitosa con token e información del usuario
        return jsonify(auth_result), 200
        
    except Exception as e:
        # Log de errores inesperados durante el login
        logger.error(f"Error durante el login: {e}", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor",
            "message": "Ocurrió un error durante el proceso de autenticación"
        }), 500

@auth.route('/auth/me', methods=['GET'])
@jwt_required()  # Requiere token JWT válido
def get_current_user():
    """
    Obtener información del usuario actual.
    
    Este endpoint permite obtener la información del usuario que está
    autenticado actualmente usando su token JWT. Es útil para:
    - Verificar que el token sigue siendo válido
    - Obtener información actualizada del usuario
    - Mostrar información del perfil en el frontend
    
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Información del usuario actual
        schema:
          type: object
          properties:
            user:
              type: object
              description: Información del usuario
      401:
        description: Token inválido o no proporcionado
      500:
        description: Error interno del servidor
    """
    try:
        # Obtener información del usuario desde el token JWT
        current_user = get_jwt_identity()
        
        # Verificar que el token contiene información válida
        if not current_user:
            return jsonify({
                "error": "Token inválido",
                "message": "No se pudo obtener la información del usuario"
            }), 401
        
        # Validar que el usuario aún existe en la base de datos
        # Esto es importante para casos donde el usuario fue eliminado
        user_info = AuthService.validate_token_payload(current_user)
        
        if not user_info:
            return jsonify({
                "error": "Usuario no encontrado",
                "message": "El usuario asociado al token no existe o está inactivo"
            }), 401
        
        # Retornar información del usuario
        return jsonify({
            "user": user_info
        }), 200
        
    except Exception as e:
        # Log de errores al obtener información del usuario
        logger.error(f"Error al obtener información del usuario: {e}", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor",
            "message": "Ocurrió un error al obtener la información del usuario"
        }), 500

@auth.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Requiere token de refresh
def refresh_token():
    """
    Refrescar token de acceso.
    
    Este endpoint permite renovar un token JWT que está próximo a expirar
    sin necesidad de que el usuario vuelva a hacer login. Es útil para:
    - Mantener sesiones activas
    - Mejorar la experiencia del usuario
    - Reducir la frecuencia de logins
    
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Nuevo token de acceso generado
        schema:
          type: object
          properties:
            token:
              type: string
              description: Nuevo token JWT
            type:
              type: string
              description: Tipo de token (siempre "Bearer")
      401:
        description: Token de refresh inválido
      500:
        description: Error interno del servidor
    """
    try:
        # Obtener información del usuario desde el token de refresh
        current_user = get_jwt_identity()
        
        if not current_user:
            return jsonify({
                "error": "Token de refresh inválido",
                "message": "No se pudo validar el token de refresh"
            }), 401
        
        # Validar que el usuario aún existe en la base de datos
        user_info = AuthService.validate_token_payload(current_user)
        
        if not user_info:
            return jsonify({
                "error": "Usuario no encontrado",
                "message": "El usuario asociado al token no existe o está inactivo"
            }), 401
        
        # Generar nuevo token de acceso
        from flask_jwt_extended import create_access_token
        from datetime import timedelta
        
        new_token = create_access_token(
            identity=user_info,
            expires_delta=timedelta(hours=8)  # Token válido por 8 horas
        )
        
        # Retornar nuevo token
        return jsonify({
            "token": new_token,
            "type": "Bearer"
        }), 200
        
    except Exception as e:
        # Log de errores al refrescar token
        logger.error(f"Error al refrescar token: {e}", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor",
            "message": "Ocurrió un error al refrescar el token"
        }), 500

# Endpoint adicional para obtener lista de usuarios (comentado por seguridad)
@auth.route('/auth/get_users', methods=['GET'])
#@jwt_required()  # Comentado para testing
def get_list_users():
    """
    Obtener una lista de usuarios. Requiere bearer token.
    
    NOTA: Este endpoint está comentado por seguridad. En producción,
    debería estar protegido con @jwt_required() y verificar permisos
    de administrador.
    
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Respuesta exitosa con la lista de usuarios
      401:
        description: Unauthorized
    """
    current_user = "test" #get_jwt_identity()  # Comentado para testing
    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Obtener lista de usuarios usando el servicio
    from core.usuarios import UsuarioCRUD
    obj_usuarios = UsuarioCRUD()
    response = obj_usuarios.obtener_todos()
    return jsonify(response), 200

@auth.route('/auth/validate', methods=['POST'])
@limiter.limit("100 per hour")  # Limitar validaciones por hora
def validate_jwt_token():
    """
    Validar token JWT y verificar que el usuario sea válido en la base de datos.
    
    Este endpoint recibe un token JWT y verifica:
    1. Que el token sea válido y no haya expirado
    2. Que el usuario del token exista en la base de datos
    3. Que el usuario esté activo (id_estatus = 1)
    4. Que la información del token coincida con la BD
    
    Es útil para:
    - Verificar la validez de tokens en el frontend
    - Validar sesiones antes de operaciones críticas
    - Refrescar información del usuario
    
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - token
          properties:
            token:
              type: string
              description: Token JWT a validar
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    responses:
      200:
        description: Token válido y usuario verificado
        schema:
          type: object
          properties:
            valid:
              type: boolean
              description: Indica si el token es válido
            user:
              type: object
              description: Información del usuario verificado
            message:
              type: string
              description: Mensaje descriptivo
      400:
        description: Token no proporcionado o formato inválido
      401:
        description: Token inválido o usuario no encontrado
      429:
        description: Demasiadas solicitudes de validación
      500:
        description: Error interno del servidor
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        
        # Validar que se proporcionó un token
        if not data or not data.get('token'):
            return jsonify({
                "valid": False,
                "error": "Token no proporcionado",
                "message": "Debe proporcionar un token JWT para validar"
            }), 400
        
        token = data.get('token')
        
        # Importar funciones necesarias para validar JWT
        from flask_jwt_extended import decode_token, get_jwt_identity
        from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
        
        try:
            # Decodificar el token JWT para obtener el payload
            # Esto verifica que el token sea válido y no haya expirado
            token_payload = decode_token(token)
            
            # Extraer la identidad del usuario del token
            user_identity = token_payload['sub']  # 'sub' contiene la información del usuario
            
            # Validar que el usuario existe en la base de datos y está activo
            user_info = AuthService.validate_token_payload(user_identity)
            
            if not user_info:
                logger.warning(f"Token válido pero usuario no encontrado en BD: {user_identity.get('username', 'unknown')}")
                return jsonify({
                    "valid": False,
                    "error": "Usuario no encontrado",
                    "message": "El usuario asociado al token no existe o está inactivo"
                }), 401
            
            # Log de validación exitosa
            logger.info(f"Token validado exitosamente para usuario: {user_info['username']}")
            
            # Retornar respuesta exitosa con información del usuario
            return jsonify({
                "valid": True,
                "user": user_info,
                "message": "Token válido y usuario verificado"
            }), 200
            
        except ExpiredSignatureError:
            # Token ha expirado
            logger.warning("Intento de validación con token expirado")
            return jsonify({
                "valid": False,
                "error": "Token expirado",
                "message": "El token ha expirado, debe renovarlo"
            }), 401
            
        except InvalidTokenError as e:
            # Token inválido por otras razones
            logger.warning(f"Intento de validación con token inválido: {str(e)}")
            return jsonify({
                "valid": False,
                "error": "Token inválido",
                "message": "El token proporcionado no es válido"
            }), 401
            
    except Exception as e:
        # Log de errores inesperados durante la validación
        logger.error(f"Error durante la validación del token: {e}", exc_info=True)
        return jsonify({
            "valid": False,
            "error": "Error interno del servidor",
            "message": "Ocurrió un error durante la validación del token"
        }), 500

@auth.route('/auth/verify', methods=['GET'])
@jwt_required()  # Requiere token JWT válido en el header
def verify_current_token():
    """
    Verificar el token JWT actual del usuario.
    
    Este endpoint verifica el token JWT que se envía en el header Authorization.
    Es similar a /auth/me pero específicamente para validación de tokens.
    
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Token válido y usuario verificado
        schema:
          type: object
          properties:
            valid:
              type: boolean
              description: Indica si el token es válido
            user:
              type: object
              description: Información del usuario verificado
            token_info:
              type: object
              description: Información adicional del token
      401:
        description: Token inválido o no proporcionado
      500:
        description: Error interno del servidor
    """
    try:
        # Obtener información del usuario desde el token JWT
        current_user = get_jwt_identity()
        
        # Verificar que el token contiene información válida
        if not current_user:
            return jsonify({
                "valid": False,
                "error": "Token inválido",
                "message": "No se pudo obtener la información del usuario del token"
            }), 401
        
        # Validar que el usuario aún existe en la base de datos
        user_info = AuthService.validate_token_payload(current_user)
        
        if not user_info:
            return jsonify({
                "valid": False,
                "error": "Usuario no encontrado",
                "message": "El usuario asociado al token no existe o está inactivo"
            }), 401
        
        # Obtener información adicional del token
        from flask_jwt_extended import get_jwt
        
        token_info = {
            "expires_at": get_jwt().get('exp'),
            "issued_at": get_jwt().get('iat'),
            "token_type": "access"
        }
        
        # Log de verificación exitosa
        logger.info(f"Token verificado exitosamente para usuario: {user_info['username']}")
        
        # Retornar respuesta exitosa
        return jsonify({
            "valid": True,
            "user": user_info,
            "token_info": token_info,
            "message": "Token válido y usuario verificado"
        }), 200
        
    except Exception as e:
        # Log de errores durante la verificación
        logger.error(f"Error durante la verificación del token: {e}", exc_info=True)
        return jsonify({
            "valid": False,
            "error": "Error interno del servidor",
            "message": "Ocurrió un error durante la verificación del token"
        }), 500

