from flask import Blueprint, jsonify, request
from core.usuarios import UsuarioCRUD


usuarios = Blueprint('usuarios', __name__)

obj_usuarios = UsuarioCRUD()

@usuarios.route('/usuarios/listar', methods=['GET'])
def listar_usuarios():
    response = obj_usuarios.obtener_todos()
    return jsonify(response), 200

@usuarios.route('/usuarios/usuario', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    response = obj_usuarios.crear_usuario(data)
    return jsonify(response), 200
