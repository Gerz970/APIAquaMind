from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta
from models.seguridad import TbUsuario
from utils.connectiondb import get_session
# Removido werkzeug.security import - usando bcrypt directamente
import logging
from flask import jsonify

# Configurar el registro de errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_access(user, password):
    """
    Valida el acceso del usuario con las credenciales proporcionadas.

    Args:
        user (str): Nombre de usuario.
        password (str): Contraseña del usuario.

    Returns:
        dict: Información del usuario y el token de acceso o un mensaje de error.
    """
    session = get_session()
    try:
        usuario = session.query(TbUsuario).filter_by(username=user).first()

        if usuario is None:
            logger.warning(f"Usuario no encontrado: {user}")
            return {"error": "Usuario o contraseña incorrectos"}

        if not usuario.verify_password(password):
            logger.warning(f"Contraseña incorrecta para el usuario: {user}")
            return {"error": "Usuario o contraseña incorrectos"}

        logger.info(f"Usuario encontrado: {usuario.nombre} {usuario.apellido_paterno}")

        access_token = create_access_token(
            identity={"user": usuario.username, "user_id": usuario.id_usuario},
            expires_delta=timedelta(hours=8)
        )

        return  {"token": access_token, "type": "Bearer"}

    except Exception as e:
        # Manejar cualquier error inesperado
        logger.error(f"Error al validar el acceso: {e}", exc_info=True)
        return {"error": "Ocurrió un error al procesar la solicitud"}
    finally:
        # Asegurarse de cerrar la sesión
        session.close()
