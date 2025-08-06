from flask import Blueprint, jsonify, request
from core.configuraciones import ConfiguracionCRUD


configuraciones = Blueprint('configuraciones', __name__)

obj_configuraciones = ConfiguracionCRUD()

def safe_to_dict(obj):
    """Convierte objetos a diccionario de forma segura."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return obj
    else:
        return str(obj)

@configuraciones.route('/configuraciones/configuracion', methods=['POST'])
def crear_configuracion():
    """Crear una nueva configuración."""
    data = request.get_json()
    response, status = obj_configuraciones.crear_configuracion(data)
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion', methods=['GET'])
def obtener_configuraciones():
    """Obtener lista de todas las configuraciones."""
    response, status = obj_configuraciones.obtener_todas()
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion/<configuracion>', methods=['PUT'])
def actualizar_configuracion(configuracion):
    """Actualizar una configuración existente por nombre de configuración."""
    data = request.get_json()
    response, status = obj_configuraciones.actualizar_configuracion(configuracion, data)
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion/<int:id_configuracion>', methods=['PUT'])
def actualizar_configuracion_por_id(id_configuracion):
    """Actualizar una configuración existente por ID."""
    data = request.get_json()
    response, status = obj_configuraciones.actualizar_por_id(id_configuracion, data)
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion/<configuracion>', methods=['DELETE'])
def eliminar_configuracion(configuracion):
    """Eliminar una configuración por nombre de configuración."""
    response, status = obj_configuraciones.eliminar_configuracion(configuracion)
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion/<int:id_configuracion>', methods=['DELETE'])
def eliminar_configuracion_por_id(id_configuracion):
    """Eliminar una configuración por ID."""
    response, status = obj_configuraciones.eliminar_por_id(id_configuracion)
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion/<configuracion>', methods=['GET'])
def obtener_configuracion(configuracion):
    """Obtener una configuración específica por nombre de configuración."""
    response, status = obj_configuraciones.obtener_por_configuracion(configuracion)
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion/id/<int:id_configuracion>', methods=['GET'])
def obtener_configuracion_por_id(id_configuracion):
    """Obtener una configuración específica por ID."""
    response, status = obj_configuraciones.obtener_por_id(id_configuracion)
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion/valor/<configuracion>', methods=['GET'])
def obtener_valor_configuracion(configuracion):
    """Obtener solo el valor de una configuración específica."""
    response, status = obj_configuraciones.obtener_valor_configuracion(configuracion)
    return jsonify(response), status

@configuraciones.route('/configuraciones/configuracion/estatus/<int:id_estatus>', methods=['GET'])
def obtener_configuraciones_por_estatus(id_estatus):
    """Obtener todas las configuraciones por estatus."""
    response, status = obj_configuraciones.obtener_por_estatus(id_estatus)
    return jsonify(response), status 