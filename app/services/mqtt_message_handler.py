"""
Manejador de mensajes MQTT para APIAquaMind.

Este módulo procesa los mensajes recibidos del broker MQTT
y los integra con el sistema de base de datos existente.

Características:
- Procesamiento de diferentes tipos de mensajes
- Integración con el sistema de nodos y eventos
- Validación de datos recibidos
- Logging detallado de operaciones
"""

import json
import logging
from datetime import datetime
from core.mqtt_data_processor import MQTTDataProcessor

class MQTTMessageHandler:
    def __init__(self):
        """
        Inicializar manejador de mensajes MQTT.
        """
        self.logger = logging.getLogger(__name__)
        self.data_processor = MQTTDataProcessor()
        
    def process_message(self, topic, payload, timestamp):
        """
        Procesar mensaje recibido según el tópico.
        
        Args:
            topic: Tópico del mensaje
            payload: Contenido del mensaje
            timestamp: Timestamp del mensaje
        """
        try:
            self.logger.info(f"Procesando mensaje de {topic}")
            
            if topic == "status/sistema":
                self.handle_system_status(payload, timestamp)
            elif topic == "sensor/flujo":
                self.handle_flow_sensor(payload, timestamp)
            elif topic.startswith("control/valvula"):
                self.handle_valve_status(topic, payload, timestamp)
            elif topic == "control/compuerta":
                self.handle_gate_status(payload, timestamp)
            elif topic.startswith("control/releb"):
                self.handle_relay_status(topic, payload, timestamp)
            else:
                self.logger.warning(f"Tópico no reconocido: {topic}")
                
        except Exception as e:
            self.logger.error(f"Error procesando mensaje de {topic}: {e}")
    
    def handle_system_status(self, payload, timestamp):
        """
        Manejar estado del sistema.
        
        Args:
            payload: Datos del estado del sistema
            timestamp: Timestamp del mensaje
        """
        try:
            # Intentar parsear como JSON
            if payload:
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    # Si no es JSON, tratar como string simple
                    data = {"status": payload}
            else:
                data = {"status": "unknown"}
            
            # Agregar timestamp
            data['timestamp'] = timestamp.isoformat()
            
            self.data_processor.save_system_status(data, timestamp)
            self.logger.info(f"Estado del sistema procesado: {data}")
            
        except Exception as e:
            self.logger.error(f"Error procesando estado del sistema: {e}")
    
    def handle_flow_sensor(self, payload, timestamp):
        """
        Manejar datos del sensor de flujo.
        
        Args:
            payload: Datos del sensor de flujo
            timestamp: Timestamp del mensaje
        """
        try:
            # Convertir a float, manejar errores
            try:
                flow_value = float(payload) if payload else 0.0
            except (ValueError, TypeError):
                self.logger.warning(f"Valor de flujo inválido: {payload}")
                flow_value = 0.0
            
            self.data_processor.save_flow_data(flow_value, timestamp)
            self.logger.info(f"Datos de flujo procesados: {flow_value} L/min")
            
        except Exception as e:
            self.logger.error(f"Error procesando datos de flujo: {e}")
    
    def handle_valve_status(self, topic, payload, timestamp):
        """
        Manejar estado de válvulas.
        
        Args:
            topic: Tópico del mensaje (contiene ID de válvula)
            payload: Estado de la válvula
            timestamp: Timestamp del mensaje
        """
        try:
            # Extraer ID de válvula del tópico
            valve_id = topic.split('/')[-1]  # Ej: "control/valvula1" -> "1"
            
            # Normalizar estado
            status = payload.upper() if payload else "UNKNOWN"
            
            # Validar estado
            valid_states = ["ON", "OFF", "OPEN", "CLOSE", "UNKNOWN"]
            if status not in valid_states:
                self.logger.warning(f"Estado de válvula inválido: {status}")
                status = "UNKNOWN"
            
            self.data_processor.save_valve_status(valve_id, status, timestamp)
            self.logger.info(f"Estado de válvula {valve_id} procesado: {status}")
            
        except Exception as e:
            self.logger.error(f"Error procesando estado de válvula: {e}")
    
    def handle_gate_status(self, payload, timestamp):
        """
        Manejar estado de compuerta.
        
        Args:
            payload: Estado de la compuerta
            timestamp: Timestamp del mensaje
        """
        try:
            # Normalizar estado
            status = payload.upper() if payload else "UNKNOWN"
            
            # Validar estado
            valid_states = ["OPEN", "CLOSE", "UNKNOWN"]
            if status not in valid_states:
                self.logger.warning(f"Estado de compuerta inválido: {status}")
                status = "UNKNOWN"
            
            self.data_processor.save_gate_status(status, timestamp)
            self.logger.info(f"Estado de compuerta procesado: {status}")
            
        except Exception as e:
            self.logger.error(f"Error procesando estado de compuerta: {e}")
    
    def handle_relay_status(self, topic, payload, timestamp):
        """
        Manejar estado de relés.
        
        Args:
            topic: Tópico del mensaje (contiene ID de relé)
            payload: Estado del relé
            timestamp: Timestamp del mensaje
        """
        try:
            # Extraer ID de relé del tópico
            relay_id = topic.split('/')[-1]  # Ej: "control/releb1" -> "1"
            
            # Normalizar estado
            status = payload.upper() if payload else "UNKNOWN"
            
            # Validar estado
            valid_states = ["ON", "OFF", "UNKNOWN"]
            if status not in valid_states:
                self.logger.warning(f"Estado de relé inválido: {status}")
                status = "UNKNOWN"
            
            self.data_processor.save_relay_status(relay_id, status, timestamp)
            self.logger.info(f"Estado de relé {relay_id} procesado: {status}")
            
        except Exception as e:
            self.logger.error(f"Error procesando estado de relé: {e}")
    
    def validate_payload(self, payload, expected_type="string"):
        """
        Validar payload recibido.
        
        Args:
            payload: Payload a validar
            expected_type: Tipo esperado (string, number, json)
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        try:
            if expected_type == "string":
                return isinstance(payload, str) and len(payload.strip()) > 0
            elif expected_type == "number":
                return isinstance(payload, (int, float)) or (isinstance(payload, str) and payload.replace('.', '').isdigit())
            elif expected_type == "json":
                json.loads(payload)
                return True
            else:
                return payload is not None
        except Exception:
            return False 