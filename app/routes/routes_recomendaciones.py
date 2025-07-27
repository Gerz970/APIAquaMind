from flask import Blueprint, jsonify, request
from core.recomendaciones import RecomendacionesCRUD


recomendaciones = Blueprint('recomendaciones', __name__)

obj_recomendaciones = RecomendacionesCRUD()

def safe_to_dict(obj):
    """Convierte objetos a diccionario de forma segura."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return obj
    else:
        return str(obj)

@recomendaciones.route('/recomendaciones/listar', methods=['GET'])
def listar_recomendaciones():
    """Obtener lista de todas las recomendaciones activas."""
    response = obj_recomendaciones.obtener_todas()
    return jsonify(response), 200

@recomendaciones.route('/recomendaciones/aleatorias/<int:cantidad>', methods=['GET'])
def obtener_recomendaciones_aleatorias(cantidad):
    """Obtener recomendaciones aleatorias según la cantidad especificada."""
    response = obj_recomendaciones.obtener_recomendaciones_aleatorias(cantidad)
    return jsonify(response), 200

@recomendaciones.route('/recomendaciones/recomendacion', methods=['POST'])
def crear_recomendacion():
    """Crear una nueva recomendación."""
    data = request.get_json()
    response, status = obj_recomendaciones.crear_recomendacion(data)
    return jsonify(response), status

@recomendaciones.route('/recomendaciones/recomendacion/<int:id_recomendacion>', methods=['PUT'])
def actualizar_recomendacion(id_recomendacion):
    """Actualizar una recomendación existente."""
    data = request.get_json()
    response, status = obj_recomendaciones.actualizar_recomendacion(id_recomendacion, data)
    return jsonify(response), status

@recomendaciones.route('/recomendaciones/recomendacion/<int:id_recomendacion>', methods=['DELETE'])
def eliminar_recomendacion(id_recomendacion):
    """Eliminar una recomendación (marcar como inactiva)."""
    response, status = obj_recomendaciones.eliminar_recomendacion(id_recomendacion)
    return jsonify(response), status

@recomendaciones.route('/recomendaciones/recomendacion/<int:id_recomendacion>/reactivar', methods=['PUT'])
def reactivar_recomendacion(id_recomendacion):
    """Reactivar una recomendación previamente eliminada."""
    response, status = obj_recomendaciones.reactivar_recomendacion(id_recomendacion)
    return jsonify(response), status

@recomendaciones.route('/recomendaciones/recomendacion/<int:id_recomendacion>', methods=['GET'])
def obtener_recomendacion(id_recomendacion):
    """Obtener una recomendación específica por ID."""
    response, status = obj_recomendaciones.obtener_por_id(id_recomendacion)
    return jsonify(response), status

