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
    
    # Validar que el JSON esté presente
    if not data:
        return jsonify({"message": "Se requiere un JSON con fecha_inicio y fecha_fin"}), 400
    
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    # Validar que los parámetros estén presentes
    if not fecha_inicio or not fecha_fin:
        return jsonify({"message": "Los campos fecha_inicio y fecha_fin son requeridos en el JSON"}), 400
    
    response, status = obj_eventos.obtener_eventos_por_fecha(fecha_inicio, fecha_fin)
    return jsonify(response), status

@eventos.route('/eventos/evento/periodo/<int:periodo>/tipo/<int:tipo>', methods=['GET'])
def obtener_eventos_periodos(periodo, tipo):
    """Obtener eventos por período y tipo específico."""
    match tipo:
        case 1:
            eventos, status = obj_eventos.obtener_eventos_ultimos_dias(periodo)
        case 2:
            eventos, status = obj_eventos.obtener_eventos_ultimos_meses(periodo)
        case 3:
            eventos, status = obj_eventos.obtener_eventos_ultimos_anios(periodo)
        case _:
            return jsonify({"message": "El parámetro 'tipo' debe ser 1 para dias, 2 para meses o 3 para años"}), 400

    return jsonify(eventos), status
