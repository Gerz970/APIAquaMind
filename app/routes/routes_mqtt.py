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
from core.nodos import NodoCRUD

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
    actualizar_estatus_nodo(data)
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

def actualizar_estatus_nodo(payload):
    """
    Actualizar el estatus de un nodo basado en el comando recibido.
    
    Args:
        payload: Payload con device y command
        
    Returns:
        dict: Resultado de la actualización o None si hay error
        
    Ejemplo de uso:
        payload = {
            "device": "valve1",
            "command": "ON"
        }
        resultado = actualizar_estatus_nodo(None, payload)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Mapeo de dispositivos a descripciones en la BD
    DEVICE_MAPPING = {
        "valve1": "Válvula 1",
        "valve2": "Válvula 2", 
        "gate": "Compuerta",
        "relay1": "Relevador B1",
        "relay2": "Relevador B2"
    }
    
    try:
        # Validar entrada
        if not payload or not isinstance(payload, dict):
            logger.error("Payload inválido o vacío")
            return None
            
        device_name = payload.get("device")
        command = payload.get("command")
        
        if not device_name or not command:
            logger.error("Campos 'device' y 'command' son requeridos")
            return None
        
        # Validar dispositivo
        if device_name not in DEVICE_MAPPING:
            logger.error(f"Dispositivo '{device_name}' no válido")
            return None
        
        # Obtener descripción del dispositivo para buscar en BD
        device_description = DEVICE_MAPPING[device_name]
        
        # Buscar nodo en la base de datos
        nodo_crud = NodoCRUD()
        nodo_obj = nodo_crud.obtener_nodo_por_descripcion(device_description)
        
        if not nodo_obj:
            logger.error(f"Nodo no encontrado para dispositivo: {device_description}")
            return None
        
        # Determinar estado según tipo de dispositivo y comando
        command_upper = command.upper()
        estatus = None
        
        # Válvulas y relés
        if device_name in ["valve1", "valve2", "relay1", "relay2"]:
            if command_upper == "ON":
                estatus = 1
            elif command_upper == "OFF":
                estatus = 0
            else:
                logger.warning(f"Comando '{command}' no válido para {device_name}")
                return None
        
        # Compuerta
        elif device_name == "gate":
            if command_upper == "ABRIR":
                estatus = 1
            elif command_upper == "CERRAR":
                estatus = 0
            else:
                logger.warning(f"Comando '{command}' no válido para {device_name}")
                return None
        
        # Actualizar nodo si se determinó un estado válido
        if estatus is not None:
            result, status = nodo_crud.actualizar_nodo(nodo_obj[0]["id_nodo"], {"id_estatus": estatus})
            
            if result:
                logger.info(f"Nodo '{device_description}' actualizado a estado {estatus} (comando: {command})")
                return {
                    "success": True,
                    "device": device_name,
                    "device_description": device_description,
                    "command": command,
                    "status": estatus,
                    "message": f"Dispositivo {device_description} actualizado a estado {estatus}"
                }
            else:
                logger.error(f"Error actualizando nodo '{device_description}'")
                return None
        else:
            logger.error(f"No se pudo determinar estado para comando '{command}' en dispositivo '{device_name}'")
            return None
            
    except Exception as e:
        logger.error(f"Error en actualizar_estatus_nodo: {e}")
        return None
