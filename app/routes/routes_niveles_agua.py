from flask import Blueprint, jsonify, request
from core.niveles_agua import NivelAguaCRUD
from datetime import datetime
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Blueprint para rutas de niveles de agua
niveles_agua = Blueprint('niveles_agua', __name__)

# Instancia del CRUD
obj_niveles_agua = NivelAguaCRUD()

def safe_to_dict(obj):
    """Convierte objetos a diccionario de forma segura."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return obj
    else:
        return str(obj)

@niveles_agua.route('/niveles-agua', methods=['POST'])
def crear_nivel_agua():
    """Crear un nuevo registro de nivel de agua."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Datos JSON requeridos"
            }), 400
        
        response, status = obj_niveles_agua.crear_nivel_agua(data)
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error creando nivel de agua: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@niveles_agua.route('/niveles-agua/<int:id_nivel>', methods=['GET'])
def obtener_nivel_agua(id_nivel):
    """Obtener un nivel de agua por ID."""
    try:
        response, status = obj_niveles_agua.obtener_nivel_agua(id_nivel)
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error obteniendo nivel de agua: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@niveles_agua.route('/niveles-agua', methods=['GET'])
def obtener_todos_niveles_agua():
    """Obtener todos los niveles de agua con paginación."""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validar parámetros
        if limit < 1 or limit > 1000:
            return jsonify({
                "success": False,
                "error": "El parámetro 'limit' debe estar entre 1 y 1000"
            }), 400
        
        if offset < 0:
            return jsonify({
                "success": False,
                "error": "El parámetro 'offset' debe ser mayor o igual a 0"
            }), 400
        
        response, status = obj_niveles_agua.obtener_todos_niveles_agua(limit, offset)
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error obteniendo niveles de agua: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@niveles_agua.route('/niveles-agua/<int:id_nivel>', methods=['PUT'])
def actualizar_nivel_agua(id_nivel):
    """Actualizar un nivel de agua existente."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Datos JSON requeridos"
            }), 400
        
        response, status = obj_niveles_agua.actualizar_nivel_agua(id_nivel, data)
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error actualizando nivel de agua: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@niveles_agua.route('/niveles-agua/<int:id_nivel>', methods=['DELETE'])
def eliminar_nivel_agua(id_nivel):
    """Eliminar un nivel de agua."""
    try:
        response, status = obj_niveles_agua.eliminar_nivel_agua(id_nivel)
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error eliminando nivel de agua: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@niveles_agua.route('/niveles-agua/por-fecha', methods=['GET'])
def obtener_niveles_por_fecha():
    """Obtener niveles de agua por rango de fechas."""
    try:
        fecha_inicio_str = request.args.get('fecha_inicio')
        fecha_fin_str = request.args.get('fecha_fin')
        
        if not fecha_inicio_str or not fecha_fin_str:
            return jsonify({
                "success": False,
                "error": "Los parámetros 'fecha_inicio' y 'fecha_fin' son requeridos"
            }), 400
        
        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio_str.replace('Z', '+00:00'))
            fecha_fin = datetime.fromisoformat(fecha_fin_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Formato de fecha inválido. Use formato ISO (YYYY-MM-DDTHH:MM:SS)"
            }), 400
        
        response, status = obj_niveles_agua.obtener_niveles_por_fecha(fecha_inicio, fecha_fin)
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error obteniendo niveles por fecha: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@niveles_agua.route('/niveles-agua/ultimo', methods=['GET'])
def obtener_ultimo_nivel():
    """Obtener el último registro de nivel de agua."""
    try:
        response, status = obj_niveles_agua.obtener_ultimo_nivel()
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error obteniendo último nivel: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@niveles_agua.route('/niveles-agua/estadisticas', methods=['GET'])
def obtener_estadisticas_nivel():
    """Obtener estadísticas de niveles de agua."""
    try:
        dias = request.args.get('dias', 7, type=int)
        
        # Validar parámetro
        if dias < 1 or dias > 365:
            return jsonify({
                "success": False,
                "error": "El parámetro 'dias' debe estar entre 1 y 365"
            }), 400
        
        response, status = obj_niveles_agua.obtener_estadisticas_nivel(dias)
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@niveles_agua.route('/niveles-agua/actual-con-historial', methods=['GET'])
def obtener_ultimo_nivel_con_historial():
    """
    Obtener el último nivel de agua con historial de los últimos 7 días.
    
    Returns:
        JSON con el último nivel de agua, interpretación y historial de 7 días
        (una lectura por día, la última de cada día)
        
    Ejemplo de respuesta:
    {
        "success": true,
        "data": {
            "distancia": 18.5,
            "desnivel": "False",
            "bomba": "False", 
            "compuerta": "False",
            "nivel_estado": "NORMAL",
            "fecha": "2024-01-15T10:30:00",
            "porcentaje_agua": 30.00
        },
        "interpretacion": {
            "nivel": "Normal",
            "descripcion": "El nivel de agua está dentro de los parámetros normales",
            "recomendacion": "No se requiere acción inmediata",
            "color": "green",
            "dispositivos": {
                "bomba": {
                    "estado": "Inactiva",
                    "descripcion": "Bomba de drenaje está detenida"
                },
                "compuerta": {
                    "estado": "Cerrada",
                    "descripcion": "Compuerta de control está cerrada"
                }
            },
            "medicion": {
                "distancia": "18.5 cm",
                "interpretacion": "Distancia desde el sensor hasta la superficie del agua"
            }
        },
        "historial_7_dias": [
            {
                "id_nivel": 123,
                "distancia": 15.5,
                "desnivel": "False",
                "bomba": "False",
                "compuerta": "False", 
                "nivel_estado": "NORMAL",
                "porcentaje_agua": 45.00,
                "fecha": "2024-01-14T15:30:00"
            }
            // Una entrada por día de los últimos 7 días (sin incluir el día actual)
        ]
    }
    """
    try:
        response, status = obj_niveles_agua.obtener_ultimo_nivel_con_historial()
        return jsonify(response), status
        
    except Exception as e:
        logger.error(f"Error obteniendo último nivel con historial: {e}")
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500 