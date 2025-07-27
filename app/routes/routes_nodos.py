from flask import Blueprint, jsonify, request
from core.nodos import NodoCRUD


nodos = Blueprint('nodos', __name__)

obj_nodos = NodoCRUD()

def safe_to_dict(obj):
    """Convierte objetos a diccionario de forma segura."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return obj
    else:
        return str(obj)

@nodos.route('/nodos/nodo', methods=['POST'])
def crear_nodo():
    """Crear un nuevo nodo."""
    data = request.get_json()
    response, status = obj_nodos.crear_nodo(data)
    return jsonify(response), status

@nodos.route('/nodos/nodo', methods=['GET'])
def obtener_nodos():
    """Obtener lista de todos los nodos."""
    response, status = obj_nodos.obtener_todos()
    return jsonify(response), status

@nodos.route('/nodos/nodo/<int:id_nodo>', methods=['PUT'])
def actualizar_nodo(id_nodo):
    """Actualizar un nodo existente."""
    data = request.get_json()
    response, status = obj_nodos.actualizar_nodo(id_nodo, data)
    return jsonify(response), status

@nodos.route('/nodos/nodo/<int:id_nodo>', methods=['DELETE'])
def eliminar_nodo(id_nodo):
    """Eliminar un nodo (marcar como inactivo)."""
    response, status = obj_nodos.eliminar_nodo(id_nodo)
    return jsonify(response), status

@nodos.route('/nodos/nodo/<int:id_nodo>', methods=['GET'])
def obtener_nodo(id_nodo):
    """Obtener un nodo específico por ID."""
    response, status = obj_nodos.obtener_por_id(id_nodo)
    return jsonify(response), status





