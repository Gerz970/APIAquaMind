from flask import Blueprint, jsonify, request
from core.usuarios import UsuarioCRUD


usuarios = Blueprint('usuarios', __name__)

obj_usuarios = UsuarioCRUD()

def safe_to_dict(obj):
    """Convierte objetos a diccionario de forma segura."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return obj
    else:
        return str(obj)

@usuarios.route('/usuarios/listar', methods=['GET'])
def listar_usuarios():
    """Obtener lista de todos los usuarios."""
    response = obj_usuarios.obtener_todos()
    return jsonify(response), 200

@usuarios.route('/usuarios/usuario', methods=['POST'])
def crear_usuario():
    """Crear un nuevo usuario."""
    data = request.get_json()
    response, status = obj_usuarios.crear_usuario(data)
    return jsonify(response), status

@usuarios.route('/usuarios/usuario/<int:id_usuario>', methods=['PUT'])
def actualizar_usuario(id_usuario):
    """Actualizar un usuario existente."""
    data = request.get_json()
    response, status = obj_usuarios.actualizar_usuario(id_usuario, data)
    return jsonify(response), status

@usuarios.route('/usuarios/usuario/<int:id_usuario>', methods=['DELETE'])
def eliminar_usuario(id_usuario):
    """Eliminar un usuario (marcar como inactivo)."""
    response, status = obj_usuarios.eliminar_usuario(id_usuario)
    return jsonify(response), status

@usuarios.route('/usuarios/usuario/<int:id_usuario>', methods=['GET'])
def obtener_usuario(id_usuario):
    """Obtener un usuario específico por ID."""
    response, status = obj_usuarios.obtener_por_id(id_usuario)
    return jsonify(response), status
