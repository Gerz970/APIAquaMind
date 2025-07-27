from flask import Blueprint, jsonify, request
from core.eventos import EventosCRUD


eventos = Blueprint('eventos', __name__)

obj_eventos = EventosCRUD()

def safe_to_dict(obj):
    """Convierte objetos a diccionario de forma segura."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return obj
    else:
        return str(obj)

@eventos.route('/eventos/evento', methods=['POST'])
def crear_evento():
    """Crear un nuevo evento."""
    evento_data = request.get_json()
    nuevo_evento, status = obj_eventos.crear_evento(evento_data)
    return jsonify(nuevo_evento), status

# Obtener todos los eventos fechas
@eventos.route('/eventos/evento/fechas', methods=['POST'])
def obtener_eventos_fechas():
    """Obtener eventos dentro de un rango de fechas específico."""
    data = request.get_json()
    response, status = obj_eventos.obtener_eventos_por_fechas(data)
    return jsonify(response), status

@eventos.route('/eventos/evento/periodo/<int:periodo>/tipo/<int:tipo>', methods=['GET'])
def obtener_eventos_periodos(periodo, tipo):
    """Obtener eventos por período y tipo específico."""
    response, status = obj_eventos.obtener_eventos_por_periodo_tipo(periodo, tipo)
    return jsonify(response), status
