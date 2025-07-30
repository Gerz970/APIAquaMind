"""
Servicio para enviar comandos MQTT a dispositivos.

Este módulo proporciona funcionalidad para enviar comandos
a válvulas, compuertas y relés a través del broker MQTT.

Características:
- Envío de comandos a dispositivos específicos
- Validación de comandos antes del envío
- Logging de comandos enviados
- Manejo de errores de comunicación
"""

import logging
from datetime import datetime

class MQTTCommandSender:
    def __init__(self, mqtt_client=None):
        """
        Inicializar servicio de envío de comandos.
        
        Args:
            mqtt_client: Cliente MQTT configurado
        """
        self.logger = logging.getLogger(__name__)
        self.mqtt_client = mqtt_client
        
    def set_mqtt_client(self, mqtt_client):
        """
        Establecer cliente MQTT.
        
        Args:
            mqtt_client: Cliente MQTT configurado
        """
        self.mqtt_client = mqtt_client
    
    def is_connected(self):
        """
        Verificar si el cliente MQTT está conectado.
        
        Returns:
            bool: True si está conectado, False en caso contrario
        """
        if self.mqtt_client:
            return self.mqtt_client.is_connected
        return False
    
    def send_command(self, topic, command):
        """
        Enviar comando a un tópico específico.
        
        Args:
            topic: Tópico donde enviar el comando
            command: Comando a enviar
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            if not self.mqtt_client:
                self.logger.error("Cliente MQTT no configurado")
                return False
            
            if not self.is_connected():
                self.logger.error("Cliente MQTT no conectado")
                return False
            
            # Validar comando
            if not self.validate_command(command):
                self.logger.error(f"Comando inválido: {command}")
                return False
            
            # Enviar comando
            success = self.mqtt_client.publish_command(topic, command)
            
            if success:
                self.log_command(topic, command, "enviado")
            else:
                self.log_command(topic, command, "error")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error enviando comando a {topic}: {e}")
            return False
    
    def send_valve_command(self, valve_id, command):
        """
        Enviar comando a una válvula específica.
        
        Args:
            valve_id: ID de la válvula
            command: Comando (ON/OFF/OPEN/CLOSE)
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        topic = f"control/valvula{valve_id}"
        return self.send_command(topic, command)
    
    def send_gate_command(self, command):
        """
        Enviar comando a la compuerta.
        
        Args:
            command: Comando (OPEN/CLOSE)
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        topic = "control/compuerta"
        return self.send_command(topic, command)
    
    def send_relay_command(self, relay_id, command):
        """
        Enviar comando a un relé específico.
        
        Args:
            relay_id: ID del relé
            command: Comando (ON/OFF)
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        topic = f"control/releb{relay_id}"
        return self.send_command(topic, command)
    
    def validate_command(self, command):
        """
        Validar comando antes del envío.
        
        Args:
            command: Comando a validar
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        if not command:
            return False
        
        command = command.upper()
        valid_commands = ["ON", "OFF", "OPEN", "CLOSE"]
        
        return command in valid_commands
    
    def log_command(self, topic, command, status):
        """
        Registrar comando enviado.
        
        Args:
            topic: Tópico del comando
            command: Comando enviado
            status: Estado del envío (enviado/error)
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'topic': topic,
            'command': command,
            'status': status
        }
        
        if status == "enviado":
            self.logger.info(f"Comando enviado: {log_entry}")
        else:
            self.logger.error(f"Error enviando comando: {log_entry}")
    
    def get_command_history(self, limit=50):
        """
        Obtener historial de comandos enviados.
        
        Args:
            limit: Número máximo de comandos a retornar
            
        Returns:
            list: Lista de comandos enviados
        """
        # Aquí implementarías la lógica para obtener
        # el historial de comandos desde la base de datos
        return []
    
    def send_bulk_commands(self, commands):
        """
        Enviar múltiples comandos en lote.
        
        Args:
            commands: Lista de comandos [(topic, command), ...]
            
        Returns:
            dict: Resultado del envío de cada comando
        """
        results = {}
        
        for topic, command in commands:
            success = self.send_command(topic, command)
            results[f"{topic}:{command}"] = success
        
        return results
    
    def get_device_status(self, device_type, device_id=None):
        """
        Obtener estado actual de un dispositivo.
        
        Args:
            device_type: Tipo de dispositivo (valve, relay, gate)
            device_id: ID del dispositivo
            
        Returns:
            dict: Estado del dispositivo
        """
        # Aquí implementarías la lógica para obtener
        # el estado actual del dispositivo desde la base de datos
        return {
            'device_type': device_type,
            'device_id': device_id,
            'status': 'unknown',
            'last_update': datetime.now().isoformat()
        } 