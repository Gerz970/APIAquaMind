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
from core.niveles_agua import NivelAguaCRUD
from core.notificaciones import NotificacionCRUD

class MQTTDataProcessor:
    def __init__(self):
        """
        Inicializar procesador de datos MQTT.
        """
        self.logger = logging.getLogger(__name__)
        self.nodos_crud = NodoCRUD()
        self.eventos_crud = EventosCRUD()
        self.niveles_agua_crud = NivelAguaCRUD()
        self.notificaciones_crud = NotificacionCRUD()

    def save_flow_data(self, flow_value, timestamp):
        """
        Guardar datos de flujo en base de datos.
        
        Args:
            flow_value: Valor del flujo en L/min
            timestamp: Timestamp de la lectura
        """
        try:
            # Crear nodo de sensor de flujo
            """nodo_data = {
                'tipo': 'sensor_flujo',
                'valor': flow_value,
                'unidad': 'L/min',
                'fecha_lectura': timestamp.isoformat(),
                'estado': 'activo',
                'descripcion': f'Sensor de flujo - Lectura: {flow_value} L/min'
            }
            """
            evento_data = {
                'id_nodo': 1,
                'fecha_evento': timestamp,
                'id_estatus': 1,
                'consumo': flow_value,
                'unidad_medida': 'L/min'
            }
            
            ##response, status = self.eventos_crud.crear_evento(evento_data)

            try:
                self.actions_for_water_level_data(evento_data, None)
            except Exception as e:
                self.logger.error(f"Error en acciones para el nivel de agua: {e}")
            
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
    
    def save_water_level_data(self, water_data, timestamp):
        """
        Guardar datos del sensor de nivel de agua.
        
        Args:
            water_data: Diccionario con datos del nivel de agua
            timestamp: Timestamp de la lectura
        """
        try:
            
            # Preparar datos para la tabla tb_niveles_agua
            nivel_data = {
                'distancia': water_data.get('distancia'),
                'desnivel': str(water_data.get('desnivel', False)),
                'bomba': str(water_data.get('bomba', False)),
                'compuerta': str(water_data.get('compuerta', False)),
                'nivel_estado': water_data.get('nivel_estado', 'UNKNOWN'),
                'porcentaje_agua': water_data.get('porcentaje_agua')
            }
            
            last_nivel_data = self.niveles_agua_crud.obtener_ultimo_nivel_agua()
            nivel_response, nivel_status = self.niveles_agua_crud.crear_nivel_agua(nivel_data)
            
            if nivel_status == 201:
                self.logger.info("Datos guardados en tabla tb_niveles_agua")
                
                # Ejecutar acciones basadas en los datos del nivel de agua
                try:
                    self.actions_for_water_level_data(water_data, last_nivel_data)
                except Exception as e:
                    self.logger.error(f"Error en acciones para el nivel de agua: {e}")
                    
            else:
                self.logger.warning(f"Error guardando en tb_niveles_agua: {nivel_response}")
                
        except Exception as e:
            self.logger.error(f"Error guardando en tabla niveles de agua: {e}")


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
        

    def actions_for_water_level_data(self, water_data, last_nivel_data):
        """
        Acciones para el nivel de agua.
        """
        try:
            # Acciones para el nivel de agua
            if water_data.get('nivel_estado') == 'BAJO' or water_data.get('nivel_estado') == 'MUY_BAJO':
                # Abrir compuerta para captacion de agua
                self.logger.info("Desnivel detectado - Abriendo compuerta")
                

                # 1. Enviar comando MQTT para abrir compuerta (opcional si MQTT está disponible)
                mqtt_success = self._send_gate_command("ABRIR")


                # 2. Actualizar estado del nodo en la base de datos (siempre se ejecuta)
                db_success = self._update_gate_node_status(1)  # 1 = Abierto

                # Verificar si hay datos del último nivel y comparar estados
                last_nivel_estado = None
                if last_nivel_data and isinstance(last_nivel_data, tuple) and len(last_nivel_data) > 0:
                    try:
                        last_nivel_estado = last_nivel_data[0].get('data', {}).get('nivel_estado')
                    except (KeyError, IndexError, TypeError):
                        self.logger.warning("Error accediendo a datos del último nivel")
                
                current_nivel_estado = water_data.get('nivel_estado')
                
                # Generar notificación solo si el estado cambió o es la primera vez
                if last_nivel_estado != current_nivel_estado or last_nivel_estado is None:
                    self.logger.info("Nivel de agua bajo - Se genera notificacion")
                    
                    try:
                        # genera notificacion de que la compuerta se ha abierto
                        self.logger.info("Generando notificacion de que la compuerta se ha abierto")
                        notificacion_data = {
                            'notificacion': f'Nivel de agua bajo {water_data.get("porcentaje_agua")}%',
                            'mensaje': 'Compuerta abierta por nivel de agua bajo',
                            'fecha_notificacion': datetime.now()
                        }
                        response, status = self.notificaciones_crud.crear_notificacion(notificacion_data)
                        
                        if status == 201:
                            self.logger.info("Notificación creada exitosamente")
                        else:
                            self.logger.warning(f"Error creando notificación: {response}")
                            
                    except Exception as e:
                        self.logger.error(f"Error creando notificación: {e}")
                
                if mqtt_success and db_success:
                    self.logger.info("Compuerta abierta exitosamente (MQTT + BD)")
                elif db_success:
                    self.logger.info("Estado de compuerta actualizado en BD (MQTT no disponible)")
                else:
                    self.logger.error("Error actualizando estado de compuerta")
                    
            elif water_data.get('desnivel') is False:
                # Cerrar compuerta cuando el nivel vuelve a la normalidad
                self.logger.info("Nivel normal detectado - Cerrando compuerta")
                
                # 1. Enviar comando MQTT para cerrar compuerta (opcional si MQTT está disponible)
                mqtt_success = self._send_gate_command("CERRAR")
                
                # 2. Actualizar estado del nodo en la base de datos (siempre se ejecuta)
                db_success = self._update_gate_node_status(0)  # 0 = Cerrado

                # Verificar si hay datos del último nivel y comparar estados
                last_nivel_estado = None
                if last_nivel_data and isinstance(last_nivel_data, tuple) and len(last_nivel_data) > 0:
                    try:
                        last_nivel_estado = last_nivel_data[0].get('data', {}).get('nivel_estado')
                    except (KeyError, IndexError, TypeError):
                        self.logger.warning("Error accediendo a datos del último nivel")
                
                current_nivel_estado = water_data.get('nivel_estado')
                
                # Generar notificación solo si el estado cambió o es la primera vez
                if last_nivel_estado != current_nivel_estado or last_nivel_estado is None:
                    self.logger.info("Nivel de agua lleno - Se genera notificacion")
                    
                    try:
                        # genera notificacion de que la compuerta se ha cerrado
                        self.logger.info("Generando notificacion de que la compuerta se ha cerrado")
                        notificacion_data = {
                            'notificacion': f'Nivel de agua alto {water_data.get("porcentaje_agua")}%',
                            'mensaje': 'Compuerta cerrada por nivel de agua alto',
                            'fecha_notificacion': datetime.now()
                        }
                        response, status = self.notificaciones_crud.crear_notificacion(notificacion_data)
                        
                        if status == 201:
                            self.logger.info("Notificación creada exitosamente")
                        else:
                            self.logger.warning(f"Error creando notificación: {response}")
                            
                    except Exception as e:
                        self.logger.error(f"Error creando notificación: {e}")

                if mqtt_success and db_success:
                    self.logger.info("Compuerta cerrada exitosamente (MQTT + BD)")
                elif db_success:
                    self.logger.info("Estado de compuerta actualizado en BD (MQTT no disponible)")
                else:
                    self.logger.error("Error actualizando estado de compuerta")
                
        except Exception as e:
            self.logger.error(f"Error en acciones para el nivel de agua: {e}")
    
    def _send_gate_command(self, command):
        """
        Enviar comando MQTT a la compuerta.
        
        Args:
            command: Comando a enviar (ABRIR/CERRAR)
        """
        try:
            # Importar el servicio de comandos MQTT
            from services.mqtt_command_sender import MQTTCommandSender
            from flask import current_app
            
            # Crear instancia del sender
            command_sender = MQTTCommandSender()
            
            # Obtener el cliente MQTT desde la aplicación Flask
            if hasattr(current_app, 'mqtt_client') and current_app.mqtt_client:
                command_sender.set_mqtt_client(current_app.mqtt_client)
            else:
                self.logger.info("Cliente MQTT no disponible en la aplicación")
                return False
            
            # Enviar comando a la compuerta
            success = command_sender.send_gate_command(command)
            
            if success:
                self.logger.info(f"Comando MQTT enviado a compuerta: {command}")
            else:
                self.logger.info(f"No se pudo enviar comando MQTT a compuerta: {command}")
            
            return success
                
        except Exception as e:
            self.logger.info(f"No se pudo conectar al MQTT para enviar comando: {command}")
            return False
    
    def _update_gate_node_status(self, status):
        """
        Actualizar el estado del nodo de la compuerta en la base de datos.
        
        Args:
            status: Estado a establecer (1 = Abierto, 0 = Cerrado)
            
        Returns:
            bool: True si se actualizó exitosamente, False en caso contrario
        """
        try:
            from core.nodos import NodoCRUD
            
            # Crear instancia de NodoCRUD
            nodo_crud = NodoCRUD()
            
            # Buscar el nodo de la compuerta por descripción
            nodo_result = nodo_crud.obtener_nodo_por_descripcion("Compuerta")
            
            if nodo_result and isinstance(nodo_result, tuple) and len(nodo_result) > 0:
                nodo_data = nodo_result[0]  # Obtener los datos del nodo
                nodo_id = nodo_data.get('id_nodo')
                
                if nodo_id:
                    # Actualizar el estado del nodo
                    result, status_code = nodo_crud.actualizar_nodo(nodo_id, {"id_estatus": status})
                    
                    if result:
                        self.logger.info(f"Estado del nodo compuerta actualizado a: {status}")
                        return True
                    else:
                        self.logger.error(f"Error actualizando estado del nodo compuerta")
                        return False
                else:
                    self.logger.error("No se pudo obtener el ID del nodo compuerta")
                    return False
            else:
                self.logger.error("Nodo compuerta no encontrado en la base de datos")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en _update_gate_node_status: {e}")
            return False
    
    def _get_configuration_value(self, config_name, default_value=None):
        """
        Obtener valor de una configuración desde la base de datos.
        
        Args:
            config_name: Nombre de la configuración
            default_value: Valor por defecto si no se encuentra
            
        Returns:
            str: Valor de la configuración o default_value
        """
        try:
            from core.configuraciones import ConfiguracionCRUD
            
            config_crud = ConfiguracionCRUD()
            result, status = config_crud.obtener_valor_configuracion(config_name)
            
            if status == 200 and isinstance(result, dict):
                return result.get('valor', default_value)
            else:
                self.logger.warning(f"Configuración '{config_name}' no encontrada, usando valor por defecto: {default_value}")
                return default_value
                
        except Exception as e:
            self.logger.error(f"Error obteniendo configuración '{config_name}': {e}")
            return default_value
    
    def generate_dummy_water_level_data(self):
        """
        Generar datos dummy para el nivel de agua cuando MQTT está apagado.
        
        Returns:
            dict: Datos dummy del nivel de agua
        """
        import random
        from datetime import datetime
        
        # Simular diferentes escenarios de nivel de agua con más variación
        scenarios = [
            # Escenario 1: Desnivel crítico (25% probabilidad)
            {
                'distancia': random.uniform(80.0, 100.0),  # Nivel muy bajo
                'desnivel': True,
                'bomba': True,  # Bomba activa para drenar
                'compuerta': True,  # Compuerta abierta
                'nivel_estado': 'CRITICO'
            },
            # Escenario 2: Nivel alto (20% probabilidad)
            {
                'distancia': random.uniform(60.0, 80.0),  # Nivel alto
                'desnivel': False,
                'bomba': random.choice([True, False]),  # Bomba puede estar activa
                'compuerta': random.choice([True, False]),  # Compuerta puede estar abierta
                'nivel_estado': 'ALTO'
            },
            # Escenario 3: Nivel normal (30% probabilidad)
            {
                'distancia': random.uniform(40.0, 60.0),  # Nivel normal
                'desnivel': False,
                'bomba': False,  # Bomba normalmente inactiva
                'compuerta': False,  # Compuerta normalmente cerrada
                'nivel_estado': 'NORMAL'
            },
            # Escenario 4: Nivel bajo (15% probabilidad)
            {
                'distancia': random.uniform(20.0, 40.0),  # Nivel bajo
                'desnivel': False,
                'bomba': False,
                'compuerta': False,
                'nivel_estado': 'BAJO'
            },
            # Escenario 5: Nivel muy bajo (10% probabilidad)
            {
                'distancia': random.uniform(10.0, 20.0),  # Nivel muy bajo
                'desnivel': False,
                'bomba': False,
                'compuerta': False,
                'nivel_estado': 'MUY_BAJO'
            }
        ]
        
        # Seleccionar escenario con pesos (probabilidades)
        weights = [0.25, 0.20, 0.30, 0.15, 0.10]  # Probabilidades para cada escenario
        selected_scenario = random.choices(scenarios, weights=weights, k=1)[0]
        
        # Agregar pequeña variación aleatoria a la distancia
        selected_scenario['distancia'] = round(selected_scenario['distancia'] + random.uniform(-1.0, 1.0), 1)
        
        # Agregar timestamp
        selected_scenario['timestamp'] = datetime.now().isoformat()
        
        self.logger.info(f"Datos dummy generados: {selected_scenario}")
        return selected_scenario
    
    def process_dummy_water_level_data(self):
        """
        Procesar datos dummy del nivel de agua cuando MQTT está apagado.
        """
        try:
            from flask import current_app
            
            # Verificar si MQTT está apagado
            mqtt_available = hasattr(current_app, 'mqtt_client') and current_app.mqtt_client
            
            if not mqtt_available:
                self.logger.info("MQTT no disponible - Procesando datos dummy del nivel de agua")
                
                # Generar datos dummy
                dummy_data = self.generate_dummy_water_level_data()
                timestamp = datetime.now()
                
                # Procesar los datos dummy
                self.save_water_level_data(dummy_data, timestamp)
                
                # Ejecutar acciones basadas en los datos dummy
                self.actions_for_water_level_data(dummy_data, None)
                
                self.logger.info("Datos dummy del nivel de agua procesados exitosamente")
                return True
            else:
                self.logger.info("MQTT disponible - No se procesan datos dummy")
                return False
                
        except Exception as e:
            self.logger.error(f"Error procesando datos dummy del nivel de agua: {e}")
            return False
