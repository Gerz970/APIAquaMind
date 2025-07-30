"""
Monitor de dispositivos para APIAquaMind.

Este módulo proporciona funcionalidad para monitorear
el estado de dispositivos de forma continua.

Características:
- Monitoreo continuo de dispositivos
- Detección de cambios de estado
- Alertas automáticas
- Logging de eventos
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from core.mqtt_data_processor import MQTTDataProcessor

class DeviceMonitor:
    def __init__(self, mqtt_client):
        """
        Inicializar monitor de dispositivos.
        
        Args:
            mqtt_client: Cliente MQTT configurado
        """
        self.mqtt_client = mqtt_client
        self.data_processor = MQTTDataProcessor()
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        self.device_states = {}
        self.alert_thresholds = {
            'flow_sensor': {'min': 0.0, 'max': 100.0},
            'valve_status': {'timeout_minutes': 30},
            'relay_status': {'timeout_minutes': 30}
        }
    
    def start_monitoring(self):
        """Iniciar monitoreo continuo de dispositivos."""
        if self.monitoring:
            self.logger.warning("Monitoreo ya está activo")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Monitoreo de dispositivos iniciado")
    
    def stop_monitoring(self):
        """Detener monitoreo continuo de dispositivos."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Monitoreo de dispositivos detenido")
    
    def _monitor_loop(self):
        """Loop principal de monitoreo continuo."""
        while self.monitoring:
            try:
                # Verificar conexión MQTT
                if not self.mqtt_client.is_connected:
                    self._handle_mqtt_disconnection()
                
                # Verificar estado de dispositivos
                self._check_device_states()
                
                # Verificar alertas
                self._check_alerts()
                
                # Procesar datos acumulados
                self._process_accumulated_data()
                
                # Esperar antes de siguiente verificación
                time.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                self.logger.error(f"Error en loop de monitoreo: {e}")
                time.sleep(60)  # Esperar más tiempo si hay error
    
    def _handle_mqtt_disconnection(self):
        """Manejar desconexión del broker MQTT."""
        self.logger.warning("Cliente MQTT desconectado, intentando reconectar...")
        
        # Intentar reconectar
        try:
            self.mqtt_client.start()
            self.logger.info("Reconexión MQTT exitosa")
        except Exception as e:
            self.logger.error(f"Error en reconexión MQTT: {e}")
    
    def _check_device_states(self):
        """Verificar estado actual de dispositivos."""
        try:
            # Obtener estado actual de dispositivos
            current_states = self.data_processor.get_all_devices_status()
            
            if current_states:
                # Comparar con estados anteriores
                for device_type, devices in current_states.items():
                    for device_id, state in devices.items():
                        device_key = f"{device_type}_{device_id}"
                        
                        if device_key in self.device_states:
                            old_state = self.device_states[device_key]
                            if state != old_state:
                                self._handle_state_change(device_type, device_id, old_state, state)
                        
                        # Actualizar estado actual
                        self.device_states[device_key] = state
                        
        except Exception as e:
            self.logger.error(f"Error verificando estados de dispositivos: {e}")
    
    def _handle_state_change(self, device_type, device_id, old_state, new_state):
        """
        Manejar cambio de estado de dispositivo.
        
        Args:
            device_type: Tipo de dispositivo
            device_id: ID del dispositivo
            old_state: Estado anterior
            new_state: Estado nuevo
        """
        try:
            self.logger.info(f"Cambio de estado detectado: {device_type} {device_id} - {old_state} -> {new_state}")
            
            # Crear evento de cambio de estado
            from core.eventos import EventosCRUD
            eventos_crud = EventosCRUD()
            
            evento_data = {
                'tipo': f'cambio_estado_{device_type}',
                'descripcion': f'{device_type.title()} {device_id} cambió de {old_state} a {new_state}',
                'fecha_evento': datetime.now().isoformat(),
                'datos_adicionales': {
                    'device_type': device_type,
                    'device_id': device_id,
                    'old_state': old_state,
                    'new_state': new_state
                }
            }
            
            response, status = eventos_crud.crear_evento(evento_data)
            
            if status == 201:
                self.logger.info(f"Evento de cambio de estado registrado para {device_type} {device_id}")
            else:
                self.logger.warning(f"Error registrando evento de cambio de estado: {response}")
                
        except Exception as e:
            self.logger.error(f"Error manejando cambio de estado: {e}")
    
    def _check_alerts(self):
        """Verificar alertas y condiciones críticas."""
        try:
            # Verificar sensores de flujo
            self._check_flow_sensor_alerts()
            
            # Verificar timeouts de dispositivos
            self._check_device_timeouts()
            
        except Exception as e:
            self.logger.error(f"Error verificando alertas: {e}")
    
    def _check_flow_sensor_alerts(self):
        """Verificar alertas del sensor de flujo."""
        try:
            # Obtener último valor del sensor de flujo
            # Aquí implementarías la lógica para obtener el valor actual
            current_flow = 0.0  # Placeholder
            
            thresholds = self.alert_thresholds['flow_sensor']
            
            if current_flow < thresholds['min']:
                self._create_alert('flow_sensor_low', f"Flujo muy bajo: {current_flow} L/min")
            elif current_flow > thresholds['max']:
                self._create_alert('flow_sensor_high', f"Flujo muy alto: {current_flow} L/min")
                
        except Exception as e:
            self.logger.error(f"Error verificando alertas de flujo: {e}")
    
    def _check_device_timeouts(self):
        """Verificar timeouts de dispositivos."""
        try:
            current_time = datetime.now()
            
            for device_key, last_update in self.device_states.items():
                if isinstance(last_update, dict) and 'last_update' in last_update:
                    last_update_time = datetime.fromisoformat(last_update['last_update'])
                    timeout_minutes = self.alert_thresholds.get('valve_status', {}).get('timeout_minutes', 30)
                    
                    if (current_time - last_update_time).total_seconds() > (timeout_minutes * 60):
                        self._create_alert('device_timeout', f"Dispositivo {device_key} sin actualización por {timeout_minutes} minutos")
                        
        except Exception as e:
            self.logger.error(f"Error verificando timeouts: {e}")
    
    def _create_alert(self, alert_type, message):
        """
        Crear alerta en el sistema.
        
        Args:
            alert_type: Tipo de alerta
            message: Mensaje de la alerta
        """
        try:
            from core.eventos import EventosCRUD
            eventos_crud = EventosCRUD()
            
            alert_data = {
                'tipo': f'alerta_{alert_type}',
                'descripcion': message,
                'fecha_evento': datetime.now().isoformat(),
                'datos_adicionales': {
                    'alert_type': alert_type,
                    'severity': 'warning'
                }
            }
            
            response, status = eventos_crud.crear_evento(alert_data)
            
            if status == 201:
                self.logger.warning(f"Alerta creada: {message}")
            else:
                self.logger.error(f"Error creando alerta: {response}")
                
        except Exception as e:
            self.logger.error(f"Error creando alerta: {e}")
    
    def _process_accumulated_data(self):
        """Procesar datos acumulados en lote."""
        try:
            # Aquí implementarías la lógica para procesar
            # datos acumulados de forma eficiente
            pass
            
        except Exception as e:
            self.logger.error(f"Error procesando datos acumulados: {e}")
    
    def get_monitoring_status(self):
        """
        Obtener estado del monitoreo.
        
        Returns:
            dict: Información del estado del monitoreo
        """
        return {
            'monitoring': self.monitoring,
            'mqtt_connected': self.mqtt_client.is_connected if self.mqtt_client else False,
            'devices_monitored': len(self.device_states),
            'last_check': datetime.now().isoformat()
        }
    
    def update_alert_thresholds(self, new_thresholds):
        """
        Actualizar umbrales de alerta.
        
        Args:
            new_thresholds: Nuevos umbrales de alerta
        """
        try:
            self.alert_thresholds.update(new_thresholds)
            self.logger.info("Umbrales de alerta actualizados")
        except Exception as e:
            self.logger.error(f"Error actualizando umbrales: {e}") 