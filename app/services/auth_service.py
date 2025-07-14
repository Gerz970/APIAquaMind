"""
Servicio de autenticación para APIAquaMind.

Este módulo contiene toda la lógica de negocio relacionada con la autenticación:
- Validación de credenciales de usuario
- Generación y validación de tokens JWT
- Verificación de estado de usuarios
- Manejo seguro de sesiones de base de datos

El servicio implementa el patrón de servicios para separar la lógica de negocio
de las rutas y modelos, facilitando el testing y mantenimiento.
"""

from flask_jwt_extended import create_access_token
from datetime import timedelta
import logging
from typing import Optional, Dict, Any
from models.seguridad import TbUsuario
from database import get_db_session, close_db_session
# Removido werkzeug.security import - usando bcrypt directamente

# Configurar logger específico para autenticación
logger = logging.getLogger(__name__)

class AuthService:
    """
    Servicio para manejar la lógica de autenticación.
    
    Esta clase encapsula toda la lógica relacionada con:
    - Autenticación de usuarios
    - Validación de tokens
    - Verificación de credenciales
    - Generación de tokens de acceso
    
    Características:
    - Métodos estáticos para facilitar el uso
    - Manejo seguro de sesiones de BD
    - Logging detallado de operaciones
    - Validación de estado de usuarios
    """
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autenticar un usuario con las credenciales proporcionadas.
        
        Este método realiza la autenticación completa:
        1. Busca el usuario en la base de datos
        2. Verifica que el usuario esté activo
        3. Valida la contraseña usando hash seguro
        4. Genera un token JWT si la autenticación es exitosa
        
        Args:
            username: Nombre de usuario (campo único en la BD)
            password: Contraseña en texto plano (se hashea para comparar)
            
        Returns:
            Dict con token de acceso e información del usuario si es exitoso,
            None si la autenticación falla
            
        Example:
            result = AuthService.authenticate_user("usuario", "contraseña")
            if result:
                token = result["token"]
                user_info = result["user"]
        """
        # Obtener una sesión de base de datos
        session = get_db_session()
        
        try:
            # Buscar el usuario por username (campo único)
            usuario = session.query(TbUsuario).filter_by(username=username).first()
            
            # Verificar que el usuario existe
            if not usuario:
                logger.warning(f"Usuario no encontrado: {username}")
                return None
            
            # Verificar que la contraseña es correcta
            # Usar el método verify_password del modelo que usa bcrypt
            if not usuario.verify_password(password):
                logger.warning(f"Contraseña incorrecta para el usuario: {username}")
                return None
            
            # Verificar que el usuario esté activo (id_estatus = 1)
            if usuario.id_estatus != 1:
                logger.warning(f"Usuario inactivo: {username}")
                return None
            
            # Log de autenticación exitosa
            logger.info(f"Usuario autenticado exitosamente: {usuario.nombre} {usuario.apellido_paterno}")
            
            # Generar token de acceso JWT
            # El token contiene información del usuario para evitar consultas adicionales
            access_token = create_access_token(
                identity={
                    "user_id": usuario.id_usuario,
                    "username": usuario.username,
                    "email": usuario.correo_electronico,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido_paterno
                },
                expires_delta=timedelta(hours=8)  # Token válido por 8 horas
            )
            
            # Retornar respuesta con token e información del usuario
            return {
                "token": access_token,
                "type": "Bearer",  # Tipo de token para el frontend
                "user": {
                    "id": usuario.id_usuario,
                    "username": usuario.username,
                    "email": usuario.correo_electronico,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido_paterno
                }
            }
            
        except Exception as e:
            # Log de errores inesperados durante la autenticación
            logger.error(f"Error durante la autenticación: {e}", exc_info=True)
            return None
        finally:
            # Importante: siempre cerrar la sesión para liberar la conexión
            close_db_session(session)
    
    @staticmethod
    def validate_token_payload(token_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validar el payload del token JWT.
        
        Este método verifica que el usuario del token aún existe en la base de datos
        y está activo. Esto es importante para casos donde:
        - El usuario fue eliminado después de obtener el token
        - El usuario fue desactivado
        - Se necesita información actualizada del usuario
        
        Args:
            token_payload: Payload del token JWT (contiene información del usuario)
            
        Returns:
            Dict con información actualizada del usuario si es válido,
            None si el usuario no existe o está inactivo
            
        Example:
            user_info = AuthService.validate_token_payload(token_payload)
            if user_info:
                # Usar información del usuario
                user_id = user_info["user_id"]
        """
        try:
            # Extraer información del token
            user_id = token_payload.get("user_id")
            username = token_payload.get("username")
            
            # Verificar que el token tiene la información requerida
            if not user_id or not username:
                logger.warning("Token payload incompleto")
                return None
            
            # Obtener sesión de base de datos
            session = get_db_session()
            
            try:
                # Verificar que el usuario aún existe y está activo
                # Esta consulta es importante para seguridad
                usuario = session.query(TbUsuario).filter_by(
                    id_usuario=user_id,
                    username=username,
                    id_estatus=1  # Solo usuarios activos
                ).first()
                
                # Si el usuario no existe o está inactivo, el token es inválido
                if not usuario:
                    logger.warning(f"Usuario del token no encontrado o inactivo: {username}")
                    return None
                
                # Retornar información actualizada del usuario
                return {
                    "user_id": usuario.id_usuario,
                    "username": usuario.username,
                    "email": usuario.correo_electronico,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido_paterno
                }
                
            finally:
                # Siempre cerrar la sesión
                close_db_session(session)
                
        except Exception as e:
            # Log de errores durante la validación
            logger.error(f"Error al validar token payload: {e}", exc_info=True)
            return None 