"""
Procesador de datos MQTT para APIAquaMind.

Este módulo integra los datos recibidos del broker MQTT
con el sistema de base de datos existente.

Características:
- Integración con el sistema de nodos y eventos
- Almacenamiento de datos de sensores
- Registro de cambios de estado de dispositivos
- Logging detallado de operaciones
"""

import logging
from datetime import datetime
from core.nodos import NodoCRUD
from core.eventos import EventosCRUD

class MQTTDataProcessor:
    def __init__(self):
        """
        Inicializar procesador de datos MQTT.
        """
        self.logger = logging.getLogger(__name__)
        self.nodos_crud = NodoCRUD()
        self.eventos_crud = EventosCRUD()
    
    def save_flow_data(self, flow_value, timestamp):
        """
        Guardar datos de flujo en base de datos.
        
        Args:
            flow_value: Valor del flujo en L/min
            timestamp: Timestamp de la lectura
        """
        try:
            # Crear nodo de sensor de flujo
            nodo_data = {
                'tipo': 'sensor_flujo',
                'valor': flow_value,
                'unidad': 'L/min',
                'fecha_lectura': timestamp.isoformat(),
                'estado': 'activo',
                'descripcion': f'Sensor de flujo - Lectura: {flow_value} L/min'
            }
            
            response, status = self.nodos_crud.crear_nodo(nodo_data)
            
            if status == 201:
                self.logger.info(f"Datos de flujo guardados exitosamente: {flow_value} L/min")
            else:
                self.logger.warning(f"Error guardando datos de flujo: {response}")
            
        except Exception as e:
            self.logger.error(f"Error guardando datos de flujo: {e}")
    
    def save_valve_status(self, valve_id, status, timestamp):
        """
        Guardar estado de válvula.
        
        Args:
            valve_id: ID de la válvula
            status: Estado de la válvula (ON/OFF/OPEN/CLOSE)
            timestamp: Timestamp del cambio
        """
        try:
            # Crear evento de cambio de estado
            evento_data = {
                'tipo': 'cambio_estado_valvula',
                'descripcion': f'Válvula {valve_id} cambió a {status}',
                'fecha_evento': timestamp.isoformat(),
                'datos_adicionales': {
                    'valve_id': valve_id,
                    'status': status,
                    'device_type': 'valve'
                }
            }
            
            response, status = self.eventos_crud.crear_evento(evento_data)
            
            if status == 201:
                self.logger.info(f"Estado de válvula {valve_id} guardado: {status}")
            else:
                self.logger.warning(f"Error guardando estado de válvula: {response}")
            
        except Exception as e:
            self.logger.error(f"Error guardando estado de válvula: {e}")
    
    def save_gate_status(self, status, timestamp):
        """
        Guardar estado de compuerta.
        
        Args:
            status: Estado de la compuerta (OPEN/CLOSE)
            timestamp: Timestamp del cambio
        """
        try:
            # Crear evento de cambio de estado
            evento_data = {
                'tipo': 'cambio_estado_compuerta',
                'descripcion': f'Compuerta cambió a {status}',
                'fecha_evento': timestamp.isoformat(),
                'datos_adicionales': {
                    'status': status,
                    'device_type': 'gate'
                }
            }
            
            response, status = self.eventos_crud.crear_evento(evento_data)
            
            if status == 201:
                self.logger.info(f"Estado de compuerta guardado: {status}")
            else:
                self.logger.warning(f"Error guardando estado de compuerta: {response}")
            
        except Exception as e:
            self.logger.error(f"Error guardando estado de compuerta: {e}")
    
    def save_relay_status(self, relay_id, status, timestamp):
        """
        Guardar estado de relé.
        
        Args:
            relay_id: ID del relé
            status: Estado del relé (ON/OFF)
            timestamp: Timestamp del cambio
        """
        try:
            # Crear evento de cambio de estado
            evento_data = {
                'tipo': 'cambio_estado_rele',
                'descripcion': f'Relé {relay_id} cambió a {status}',
                'fecha_evento': timestamp.isoformat(),
                'datos_adicionales': {
                    'relay_id': relay_id,
                    'status': status,
                    'device_type': 'relay'
                }
            }
            
            response, status = self.eventos_crud.crear_evento(evento_data)
            
            if status == 201:
                self.logger.info(f"Estado de relé {relay_id} guardado: {status}")
            else:
                self.logger.warning(f"Error guardando estado de relé: {response}")
            
        except Exception as e:
            self.logger.error(f"Error guardando estado de relé: {e}")
    
    def save_system_status(self, data, timestamp):
        """
        Guardar estado del sistema.
        
        Args:
            data: Datos del estado del sistema
            timestamp: Timestamp del estado
        """
        try:
            # Crear evento de estado del sistema
            evento_data = {
                'tipo': 'estado_sistema',
                'descripcion': f'Estado del sistema: {data.get("status", "unknown")}',
                'fecha_evento': timestamp.isoformat(),
                'datos_adicionales': data
            }
            
            response, status = self.eventos_crud.crear_evento(evento_data)
            
            if status == 201:
                self.logger.info(f"Estado del sistema guardado: {data.get('status', 'unknown')}")
            else:
                self.logger.warning(f"Error guardando estado del sistema: {response}")
            
        except Exception as e:
            self.logger.error(f"Error guardando estado del sistema: {e}")
    
    def get_device_consumption(self, device_type, device_id=None, days=30):
        """
        Obtener consumo de un dispositivo específico.
        
        Args:
            device_type: Tipo de dispositivo (valve, relay, gate)
            device_id: ID del dispositivo (opcional)
            days: Número de días a consultar
            
        Returns:
            dict: Datos de consumo del dispositivo
        """
        try:
            # Consultar eventos del dispositivo
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Aquí implementarías la lógica para calcular el consumo
            # basado en los eventos registrados
            
            consumption_data = {
                'device_type': device_type,
                'device_id': device_id,
                'period_days': days,
                'total_events': 0,
                'status_changes': 0,
                'last_status': 'unknown'
            }
            
            self.logger.info(f"Consumo calculado para {device_type} {device_id}")
            return consumption_data
            
        except Exception as e:
            self.logger.error(f"Error calculando consumo: {e}")
            return None
    
    def get_all_devices_status(self):
        """
        Obtener estado de todos los dispositivos.
        
        Returns:
            dict: Estado de todos los dispositivos
        """
        try:
            # Aquí implementarías la lógica para obtener
            # el estado actual de todos los dispositivos
            # basado en los últimos eventos registrados
            
            devices_status = {
                'valves': {},
                'relays': {},
                'gates': {},
                'sensors': {}
            }
            
            self.logger.info("Estado de dispositivos obtenido")
            return devices_status
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado de dispositivos: {e}")
            return None 