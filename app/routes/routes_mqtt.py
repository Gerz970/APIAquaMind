"""
Rutas para control MQTT de dispositivos en APIAquaMind.

Este módulo proporciona APIs para controlar válvulas, compuertas
y relés a través del broker MQTT.

Características:
- Control de dispositivos específicos
- Validación de comandos
- Autenticación JWT requerida
- Logging de operaciones
- Documentación automática con Swagger
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.mqtt_command_sender import MQTTCommandSender
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Blueprint para rutas MQTT
mqtt_control = Blueprint('mqtt_control', __name__)

# Instancia del servicio de comandos
command_sender = MQTTCommandSender()

@mqtt_control.route('/mqtt/status', methods=['GET'])
def mqtt_status():
    """
    Obtener estado del cliente MQTT.
    
    Returns:
        JSON con información del estado de conexión
    """
    try:
        # Verificar si MQTT está habilitado en la configuración
        mqtt_enabled = current_app.config.get('MQTT_ENABLED', True)
        
        if not mqtt_enabled:
            return jsonify({
                "connected": False,
                "enabled": False,
                "message": "MQTT está deshabilitado por configuración"
            }), 200
        
        if hasattr(current_app, 'mqtt_client') and current_app.mqtt_client is not None:
            status = current_app.mqtt_client.get_connection_status()
            status["enabled"] = True
            return jsonify(status), 200
        else:
            return jsonify({
                "connected": False,
                "enabled": True,
                "error": "Cliente MQTT no inicializado"
            }), 500
    except Exception as e:
        logger.error(f"Error obteniendo estado MQTT: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/control/valvula/<int:valve_id>', methods=['POST'])
@jwt_required()
def control_valve(valve_id):
    """
    Controlar válvula específica.
    
    Args:
        valve_id: ID de la válvula a controlar
        
    Body:
        {
            "command": "ON" | "OFF" | "OPEN" | "CLOSE"
        }
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Datos JSON requeridos"
            }), 400
        
        command = data.get('command')
        if not command:
            return jsonify({
                "error": "Campo 'command' requerido"
            }), 400
        
        # Configurar cliente MQTT si no está configurado
        if hasattr(current_app, 'mqtt_client'):
            command_sender.set_mqtt_client(current_app.mqtt_client)
        
        # Enviar comando
        success = command_sender.send_valve_command(valve_id, command)
        
        if success:
            return jsonify({
                "message": f"Comando {command} enviado a válvula {valve_id}",
                "valve_id": valve_id,
                "command": command,
                "status": "enviado"
            }), 200
        else:
            return jsonify({
                "error": "Error enviando comando",
                "valve_id": valve_id,
                "command": command
            }), 500
            
    except Exception as e:
        logger.error(f"Error controlando válvula {valve_id}: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/control/compuerta', methods=['POST'])
@jwt_required()
def control_gate():
    """
    Controlar compuerta.
    
    Body:
        {
            "command": "OPEN" | "CLOSE"
        }
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Datos JSON requeridos"
            }), 400
        
        command = data.get('command')
        if not command:
            return jsonify({
                "error": "Campo 'command' requerido"
            }), 400
        
        # Configurar cliente MQTT si no está configurado
        if hasattr(current_app, 'mqtt_client'):
            command_sender.set_mqtt_client(current_app.mqtt_client)
        
        # Enviar comando
        success = command_sender.send_gate_command(command)
        
        if success:
            return jsonify({
                "message": f"Comando {command} enviado a compuerta",
                "command": command,
                "status": "enviado"
            }), 200
        else:
            return jsonify({
                "error": "Error enviando comando",
                "command": command
            }), 500
            
    except Exception as e:
        logger.error(f"Error controlando compuerta: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/control/rele/<int:relay_id>', methods=['POST'])
@jwt_required()
def control_relay(relay_id):
    """
    Controlar relé específico.
    
    Args:
        relay_id: ID del relé a controlar
        
    Body:
        {
            "command": "ON" | "OFF"
        }
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Datos JSON requeridos"
            }), 400
        
        command = data.get('command')
        if not command:
            return jsonify({
                "error": "Campo 'command' requerido"
            }), 400
        
        # Configurar cliente MQTT si no está configurado
        if hasattr(current_app, 'mqtt_client'):
            command_sender.set_mqtt_client(current_app.mqtt_client)
        
        # Enviar comando
        success = command_sender.send_relay_command(relay_id, command)
        
        if success:
            return jsonify({
                "message": f"Comando {command} enviado a relé {relay_id}",
                "relay_id": relay_id,
                "command": command,
                "status": "enviado"
            }), 200
        else:
            return jsonify({
                "error": "Error enviando comando",
                "relay_id": relay_id,
                "command": command
            }), 500
            
    except Exception as e:
        logger.error(f"Error controlando relé {relay_id}: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/devices/status', methods=['GET'])
@jwt_required()
def get_devices_status():
    """
    Obtener estado de todos los dispositivos.
    
    Returns:
        JSON con estado de todos los dispositivos
    """
    try:
        # Aquí implementarías la lógica para obtener
        # el estado actual de todos los dispositivos
        devices_status = {
            "valves": {
                "1": {"status": "OFF", "last_update": "2024-01-01T00:00:00"},
                "2": {"status": "ON", "last_update": "2024-01-01T00:00:00"}
            },
            "relays": {
                "1": {"status": "OFF", "last_update": "2024-01-01T00:00:00"},
                "2": {"status": "ON", "last_update": "2024-01-01T00:00:00"}
            },
            "gate": {
                "status": "CLOSE", "last_update": "2024-01-01T00:00:00"
            },
            "sensors": {
                "flow": {"value": 0.0, "unit": "L/min", "last_update": "2024-01-01T00:00:00"}
            }
        }
        
        return jsonify(devices_status), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de dispositivos: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/devices/consumption/<device_type>/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device_consumption(device_type, device_id):
    """
    Obtener consumo de un dispositivo específico.
    
    Args:
        device_type: Tipo de dispositivo (valve, relay, gate)
        device_id: ID del dispositivo
        
    Query Parameters:
        days: Número de días a consultar (opcional, default: 30)
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        # Aquí implementarías la lógica para calcular
        # el consumo del dispositivo
        consumption_data = {
            "device_type": device_type,
            "device_id": device_id,
            "period_days": days,
            "total_events": 0,
            "status_changes": 0,
            "last_status": "unknown",
            "usage_hours": 0
        }
        
        return jsonify(consumption_data), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo consumo de dispositivo: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/commands/history', methods=['GET'])
@jwt_required()
def get_command_history():
    """
    Obtener historial de comandos enviados.
    
    Query Parameters:
        limit: Número máximo de comandos a retornar (opcional, default: 50)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        
        # Aquí implementarías la lógica para obtener
        # el historial de comandos desde la base de datos
        command_history = []
        
        return jsonify({
            "commands": command_history,
            "total": len(command_history),
            "limit": limit
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de comandos: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/commands/bulk', methods=['POST'])
@jwt_required()
def send_bulk_commands():
    """
    Enviar múltiples comandos en lote.
    
    Body:
        {
            "commands": [
                {"topic": "control/valvula1", "command": "ON"},
                {"topic": "control/releb1", "command": "OFF"}
            ]
        }
    """
    try:
        data = request.get_json()
        if not data or 'commands' not in data:
            return jsonify({
                "error": "Campo 'commands' requerido"
            }), 400
        
        commands = data['commands']
        if not isinstance(commands, list):
            return jsonify({
                "error": "Campo 'commands' debe ser una lista"
            }), 400
        
        # Configurar cliente MQTT si no está configurado
        if hasattr(current_app, 'mqtt_client'):
            command_sender.set_mqtt_client(current_app.mqtt_client)
        
        # Enviar comandos en lote
        results = {}
        for cmd in commands:
            topic = cmd.get('topic')
            command = cmd.get('command')
            
            if topic and command:
                success = command_sender.send_command(topic, command)
                results[f"{topic}:{command}"] = success
            else:
                results[f"{topic}:{command}"] = False
        
        return jsonify({
            "message": "Comandos en lote procesados",
            "results": results,
            "total_commands": len(commands),
            "successful": sum(1 for success in results.values() if success)
        }), 200
        
    except Exception as e:
        logger.error(f"Error enviando comandos en lote: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/monitoring/status', methods=['GET'])
@jwt_required()
def get_monitoring_status():
    """
    Obtener estado del monitoreo de dispositivos.
    
    Returns:
        JSON con información del estado del monitoreo
    """
    try:
        if hasattr(current_app, 'device_monitor'):
            status = current_app.device_monitor.get_monitoring_status()
            return jsonify(status), 200
        else:
            return jsonify({
                "monitoring": False,
                "error": "Monitor de dispositivos no inicializado"
            }), 500
    except Exception as e:
        logger.error(f"Error obteniendo estado de monitoreo: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/monitoring/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """
    Obtener alertas activas del sistema.
    
    Query Parameters:
        limit: Número máximo de alertas a retornar (opcional, default: 50)
        severity: Filtrar por severidad (warning, error, critical)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        severity = request.args.get('severity')
        
        # Aquí implementarías la lógica para obtener
        # las alertas desde la base de datos
        alerts = []
        
        return jsonify({
            "alerts": alerts,
            "total": len(alerts),
            "limit": limit,
            "severity_filter": severity
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo alertas: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/monitoring/thresholds', methods=['PUT'])
@jwt_required()
def update_alert_thresholds():
    """
    Actualizar umbrales de alerta.
    
    Body:
        {
            "flow_sensor": {"min": 0.0, "max": 100.0},
            "valve_status": {"timeout_minutes": 30},
            "relay_status": {"timeout_minutes": 30}
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Datos JSON requeridos"
            }), 400
        
        if hasattr(current_app, 'device_monitor'):
            current_app.device_monitor.update_alert_thresholds(data)
            return jsonify({
                "message": "Umbrales de alerta actualizados",
                "thresholds": data
            }), 200
        else:
            return jsonify({
                "error": "Monitor de dispositivos no inicializado"
            }), 500
            
    except Exception as e:
        logger.error(f"Error actualizando umbrales: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500 

@mqtt_control.route('/mqtt/enable', methods=['POST'])
@jwt_required()
def enable_mqtt():
    """
    Habilitar el cliente MQTT.
    
    Returns:
        JSON con el estado de la operación
    """
    try:
        if not hasattr(current_app, 'mqtt_client') or current_app.mqtt_client is None:
            # Intentar inicializar el cliente MQTT
            from app import initialize_mqtt_client
            initialize_mqtt_client(current_app)
            
            if hasattr(current_app, 'mqtt_client') and current_app.mqtt_client is not None:
                return jsonify({
                    "message": "Cliente MQTT habilitado exitosamente",
                    "status": "enabled",
                    "connection": current_app.mqtt_client.get_connection_status()
                }), 200
            else:
                return jsonify({
                    "error": "No se pudo habilitar el cliente MQTT",
                    "status": "disabled"
                }), 500
        else:
            return jsonify({
                "message": "Cliente MQTT ya está habilitado",
                "status": "enabled",
                "connection": current_app.mqtt_client.get_connection_status()
            }), 200
            
    except Exception as e:
        logger.error(f"Error habilitando MQTT: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/disable', methods=['POST'])
@jwt_required()
def disable_mqtt():
    """
    Deshabilitar el cliente MQTT.
    
    Returns:
        JSON con el estado de la operación
    """
    try:
        if hasattr(current_app, 'mqtt_client') and current_app.mqtt_client is not None:
            # Detener el cliente MQTT
            current_app.mqtt_client.stop()
            
            # Limpiar las referencias
            current_app.mqtt_client = None
            current_app.mqtt_message_handler = None
            current_app.device_monitor = None
            
            return jsonify({
                "message": "Cliente MQTT deshabilitado exitosamente",
                "status": "disabled"
            }), 200
        else:
            return jsonify({
                "message": "Cliente MQTT ya está deshabilitado",
                "status": "disabled"
            }), 200
            
    except Exception as e:
        logger.error(f"Error deshabilitando MQTT: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

@mqtt_control.route('/mqtt/config', methods=['GET'])
@jwt_required()
def get_mqtt_config():
    """
    Obtener configuración actual del MQTT.
    
    Returns:
        JSON con la configuración MQTT (sin credenciales sensibles)
    """
    try:
        config = {
            "enabled": current_app.config.get('MQTT_ENABLED', True),
            "broker_host": current_app.config.get('MQTT_BROKER_HOST'),
            "broker_port": current_app.config.get('MQTT_BROKER_PORT'),
            "client_id": current_app.config.get('MQTT_CLIENT_ID'),
            "use_ssl": current_app.config.get('MQTT_USE_SSL', True),
            "version": current_app.config.get('MQTT_VERSION', 5),
            "topics": current_app.config.get('MQTT_TOPICS', {}),
            "monitoring_interval": current_app.config.get('MQTT_MONITORING_INTERVAL', 30),
            "data_retention_days": current_app.config.get('MQTT_DATA_RETENTION_DAYS', 90)
        }
        
        return jsonify(config), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración MQTT: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500 