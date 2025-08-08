from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from core.notificaciones import NotificacionCRUD
from datetime import datetime

notificaciones = Blueprint('notificaciones', __name__)

obj_notificaciones = NotificacionCRUD()

# Crear instancia de Limiter para este blueprint
limiter = Limiter(
    get_remote_address,
    default_limits=["100 per hour"]
)

def safe_to_dict(obj):
    """Convierte objetos a diccionario de forma segura."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return obj
    else:
        return str(obj)

@notificaciones.route('/notificaciones/notificacion', methods=['POST'])
@limiter.exempt  # Sin rate limit
def crear_notificacion():
    """Crear una nueva notificación."""
    data = request.get_json()
    response, status = obj_notificaciones.crear_notificacion(data)
    return jsonify(response), status

@notificaciones.route('/notificaciones/notificacion', methods=['GET'])
@limiter.exempt  # Sin rate limit
def obtener_notificaciones():
    """Obtener lista de todas las notificaciones."""
    response, status = obj_notificaciones.obtener_todas()
    return jsonify(response), status

@notificaciones.route('/notificaciones/notificacion/<int:id_notificacion>', methods=['PUT'])
@limiter.exempt  # Sin rate limit
def actualizar_notificacion(id_notificacion):
    """Actualizar una notificación existente."""
    data = request.get_json()
    response, status = obj_notificaciones.actualizar_notificacion(id_notificacion, data)
    return jsonify(response), status

@notificaciones.route('/notificaciones/notificacion/<int:id_notificacion>', methods=['DELETE'])
@limiter.exempt  # Sin rate limit
def eliminar_notificacion(id_notificacion):
    """Eliminar una notificación."""
    response, status = obj_notificaciones.eliminar_notificacion(id_notificacion)
    return jsonify(response), status

@notificaciones.route('/notificaciones/notificacion/<int:id_notificacion>', methods=['GET'])
@limiter.exempt  # Sin rate limit
def obtener_notificacion(id_notificacion):
    """Obtener una notificación específica por ID."""
    response, status = obj_notificaciones.obtener_por_id(id_notificacion)
    return jsonify(response), status

@notificaciones.route('/notificaciones/estatus/<int:id_estatus>', methods=['GET'])
@limiter.exempt  # Sin rate limit
def obtener_notificaciones_por_estatus(id_estatus):
    """Obtener notificaciones por estatus."""
    response, status = obj_notificaciones.obtener_por_estatus(id_estatus)
    return jsonify(response), status

@notificaciones.route('/notificaciones/fecha', methods=['GET'])
@limiter.exempt  # Sin rate limit
def obtener_notificaciones_por_fecha():
    """Obtener notificaciones por rango de fechas."""
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    if not fecha_inicio_str:
        return jsonify({"message": "Se requiere fecha_inicio"}), 400
    
    try:
        fecha_inicio = datetime.fromisoformat(fecha_inicio_str.replace('Z', '+00:00'))
        fecha_fin = None
        
        if fecha_fin_str:
            fecha_fin = datetime.fromisoformat(fecha_fin_str.replace('Z', '+00:00'))
        
        response, status = obj_notificaciones.obtener_por_fecha(fecha_inicio, fecha_fin)
        return jsonify(response), status
    except ValueError as e:
        return jsonify({"message": "Formato de fecha inválido", "error": str(e)}), 400 