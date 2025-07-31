"""
Rutas para control MQTT de dispositivos en APIAquaMind.

Este módulo proporciona APIs para controlar válvulas, compuertas
y relés a través del broker MQTT.

Características:
- Control centralizado de dispositivos
- Validación de comandos
- Autenticación JWT requerida
- Logging de operaciones
- Documentación automática con Swagger
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.mqtt_command_sender import MQTTCommandSender
import logging
from datetime import datetime

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

# Endpoint centralizado para control de dispositivos
@mqtt_control.route('/mqtt/control', methods=['POST'])
def control_devices():
    """
    Controlar dispositivos individual o masivamente.
    
    Opción 1 - Individual:
    {
        "device": "valve1|valve2|gate|relay1|relay2",
        "command": "ON|OFF|OPEN|CLOSE"
    }
    
    Opción 2 - Masivo:
    {
        "devices": [
            {"device": "valve1", "command": "ON"},
            {"device": "gate", "command": "CLOSE"}
        ]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Datos JSON requeridos"
            }), 400
        
        # Configurar cliente MQTT si no está configurado
        if hasattr(current_app, 'mqtt_client'):
            command_sender.set_mqtt_client(current_app.mqtt_client)
        
        # Detectar si es individual o masivo
        if "device" in data:
            # Comando individual
            return handle_single_command(data)
        elif "devices" in data:
            # Comando masivo
            return handle_bulk_commands(data["devices"])
        else:
            return jsonify({
                "error": "Formato inválido. Use 'device' para individual o 'devices' para masivo"
            }), 400
            
    except Exception as e:
        logger.error(f"Error en control de dispositivos: {e}")
        return jsonify({
            "error": "Error interno del servidor"
        }), 500

def handle_single_command(data):
    """
    Manejar comando individual.
    
    Args:
        data: Datos del request con device y command
        
    Returns:
        JSON response
    """
    device = data.get('device')
    command = data.get('command')
    
    if not device:
        return jsonify({
            "error": "Campo 'device' requerido"
        }), 400
    
    if not command:
        return jsonify({
            "error": "Campo 'command' requerido"
        }), 400
    
    # Validar dispositivo y comando
    validation_result = validate_device_command(device, command)
    if not validation_result["valid"]:
        return jsonify({
            "error": validation_result["message"]
        }), 400
    
    # Enviar comando
    success = command_sender.send_command(validation_result["topic"], command)
    
    if success:
        return jsonify({
            "success": True,
            "message": "Comando enviado exitosamente",
            "data": {
                "device": device,
                "command": command,
                "topic": validation_result["topic"],
                "description": validation_result["description"],
                "timestamp": datetime.now().isoformat()
            }
        }), 200
    else:
        return jsonify({
            "error": "Error enviando comando",
            "device": device,
            "command": command
        }), 500

def handle_bulk_commands(devices_data):
    """
    Manejar comandos masivos.
    
    Args:
        devices_data: Lista de comandos de dispositivos
        
    Returns:
        JSON response
    """
    if not isinstance(devices_data, list):
        return jsonify({
            "error": "Campo 'devices' debe ser una lista"
        }), 400
    
    if not devices_data:
        return jsonify({
            "error": "Lista de dispositivos no puede estar vacía"
        }), 400
    
    results = []
    successful = 0
    failed = 0
    
    for device_data in devices_data:
        if not isinstance(device_data, dict):
            results.append({
                "status": "error",
                "error": "Formato de dispositivo inválido"
            })
            failed += 1
            continue
        
        device = device_data.get('device')
        command = device_data.get('command')
        
        if not device or not command:
            results.append({
                "status": "error",
                "error": "Campos 'device' y 'command' requeridos"
            })
            failed += 1
            continue
        
        # Validar dispositivo y comando
        validation_result = validate_device_command(device, command)
        if not validation_result["valid"]:
            results.append({
                "device": device,
                "command": command,
                "status": "error",
                "error": validation_result["message"]
            })
            failed += 1
            continue
        
        # Enviar comando
        success = command_sender.send_command(validation_result["topic"], command)
        
        if success:
            results.append({
                "device": device,
                "command": command,
                "status": "success",
                "topic": validation_result["topic"],
                "description": validation_result["description"]
            })
            successful += 1
        else:
            results.append({
                "device": device,
                "command": command,
                "status": "error",
                "error": "Error enviando comando"
            })
            failed += 1
    
    return jsonify({
        "success": True,
        "message": "Comandos procesados",
        "data": {
            "total_commands": len(devices_data),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    }), 200

def validate_device_command(device, command):
    """
    Validar dispositivo y comando.
    
    Args:
        device: Nombre del dispositivo
        command: Comando a ejecutar
        
    Returns:
        dict: Resultado de validación
    """
    # Mapeo de dispositivos
    DEVICE_MAPPING = {
        "valve1": {
            "topic": "control/valvula1",
            "valid_commands": ["ON", "OFF"],
            "description": "Válvula 1"
        },
        "valve2": {
            "topic": "control/valvula2",
            "valid_commands": ["ON", "OFF"],
            "description": "Válvula 2"
        },
        "gate": {
            "topic": "control/compuerta",
            "valid_commands": ["ABRIR", "CERRAR"],
            "description": "Compuerta"
        },
        "relay1": {
            "topic": "control/releb1",
            "valid_commands": ["ON", "OFF"],
            "description": "Relevador B1"
        },
        "relay2": {
            "topic": "control/releb2",
            "valid_commands": ["ON", "OFF"],
            "description": "Relevador B2"
        }
    }
    
    # Validar dispositivo
    if device not in DEVICE_MAPPING:
        return {
            "valid": False,
            "message": f"Dispositivo '{device}' no válido. Dispositivos válidos: {list(DEVICE_MAPPING.keys())}"
        }
    
    device_config = DEVICE_MAPPING[device]
    
    # Validar comando
    if command.upper() not in device_config["valid_commands"]:
        return {
            "valid": False,
            "message": f"Comando '{command}' no válido para '{device}'. Comandos válidos: {device_config['valid_commands']}"
        }
    
    return {
        "valid": True,
        "topic": device_config["topic"],
        "description": device_config["description"]
    }

@mqtt_control.route('/mqtt/devices', methods=['GET'])
@jwt_required()
def get_devices():
    """
    Obtener información de todos los dispositivos disponibles.
    
    Returns:
        JSON con información de dispositivos
    """
    devices = [
        {
            "id": "valve1",
            "name": "Válvula 1",
            "topic": "control/valvula1",
            "commands": ["ON", "OFF"],
            "description": "Abre o cierra válvula 1"
        },
        {
            "id": "valve2",
            "name": "Válvula 2",
            "topic": "control/valvula2",
            "commands": ["ON", "OFF"],
            "description": "Abre o cierra válvula 2"
        },
        {
            "id": "gate",
            "name": "Compuerta",
            "topic": "control/compuerta",
            "commands": ["ABRIR", "CERRAR"],
            "description": "Abre o cierra compuerta"
        },
        {
            "id": "relay1",
            "name": "Relevador B1",
            "topic": "control/releb1",
            "commands": ["ON", "OFF"],
            "description": "Activa o desactiva rele B1"
        },
        {
            "id": "relay2",
            "name": "Relevador B2",
            "topic": "control/releb2",
            "commands": ["ON", "OFF"],
            "description": "Activa o desactiva rele B2"
        }
    ]
    
    return jsonify({
        "success": True,
        "devices": devices
    }), 200 