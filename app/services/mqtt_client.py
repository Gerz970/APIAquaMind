"""
Cliente MQTT para HiveMQ Cloud en APIAquaMind.

Este módulo implementa un cliente MQTT que se conecta a HiveMQ Cloud
para recibir datos de sensores y dispositivos en tiempo real.

Características:
- Conexión SSL/TLS segura a HiveMQ Cloud
- Protocolo MQTT v5
- Reconexión automática
- Procesamiento de mensajes en tiempo real
- Logging detallado de operaciones
"""

import paho.mqtt.client as mqtt
import json
import logging
from threading import Thread
import time
from datetime import datetime

class HiveMQClient:
    def __init__(self, config):
        """
        Inicializar cliente MQTT para HiveMQ Cloud.
        
        Args:
            config: Configuración de la aplicación Flask
        """
        self.config = config
        self.client = mqtt.Client(
            client_id=config['MQTT_CLIENT_ID'],
            protocol=mqtt.MQTTv5
        )
        self.logger = logging.getLogger(__name__)
        self.message_handler = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    def setup_ssl(self):
        """Configurar SSL para HiveMQ Cloud."""
        try:
            self.client.tls_set()
            self.client.tls_insecure_set(False)
            self.logger.info("SSL configurado para HiveMQ Cloud")
        except Exception as e:
            self.logger.error(f"Error configurando SSL: {e}")
    
    def on_connect(self, client, userdata, flags, rc, properties=None):
        """
        Callback ejecutado cuando se conecta al broker.
        
        Args:
            client: Cliente MQTT
            userdata: Datos de usuario
            flags: Flags de conexión
            rc: Código de resultado
            properties: Propiedades MQTT v5
        """
        if rc == 0:
            self.is_connected = True
            self.reconnect_attempts = 0
            self.logger.info("Conectado exitosamente a HiveMQ Cloud")
            self.subscribe_to_topics()
        else:
            self.is_connected = False
            self.logger.error(f"Error de conexión: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """
        Callback ejecutado cuando se desconecta del broker.
        
        Args:
            client: Cliente MQTT
            userdata: Datos de usuario
            rc: Código de resultado
        """
        self.is_connected = False
        self.logger.warning(f"Desconectado del broker MQTT: {rc}")
        
        # Intentar reconectar si no es una desconexión intencional
        if rc != 0 and self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            self.logger.info(f"Intentando reconectar... (intento {self.reconnect_attempts})")
            time.sleep(5)  # Esperar antes de reconectar
            self.start()
    
    def subscribe_to_topics(self):
        """Suscribirse a todos los tópicos necesarios."""
        topics = [
            (self.config['MQTT_TOPICS']['SYSTEM_STATUS'], 1),
            (self.config['MQTT_TOPICS']['FLOW_SENSOR'], 1),
            (f"{self.config['MQTT_TOPICS']['VALVE_CONTROL']}1", 1),
            (f"{self.config['MQTT_TOPICS']['VALVE_CONTROL']}2", 1),
            (self.config['MQTT_TOPICS']['GATE_CONTROL'], 1),
            (f"{self.config['MQTT_TOPICS']['RELAY_CONTROL']}1", 1),
            (f"{self.config['MQTT_TOPICS']['RELAY_CONTROL']}2", 1)
        ]
        
        for topic, qos in topics:
            try:
                self.client.subscribe(topic, qos)
                self.logger.info(f"Suscrito a: {topic} (QoS: {qos})")
            except Exception as e:
                self.logger.error(f"Error suscribiéndose a {topic}: {e}")
    
    def on_message(self, client, userdata, msg):
        """
        Callback ejecutado cuando se recibe un mensaje.
        
        Args:
            client: Cliente MQTT
            userdata: Datos de usuario
            msg: Mensaje recibido
        """
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            timestamp = datetime.now()
            
            self.logger.info(f"Mensaje recibido en {topic}: {payload}")
            
            # Procesar según el tópico
            if self.message_handler:
                self.message_handler.process_message(topic, payload, timestamp)
            else:
                self.logger.warning("No hay manejador de mensajes configurado")
                
        except Exception as e:
            self.logger.error(f"Error procesando mensaje: {e}")
    
    def on_log(self, client, userdata, level, buf):
        """
        Callback para logging del cliente MQTT.
        
        Args:
            client: Cliente MQTT
            userdata: Datos de usuario
            level: Nivel de log
            buf: Mensaje de log
        """
        if level == mqtt.MQTT_LOG_ERR:
            self.logger.error(f"MQTT Error: {buf}")
        elif level == mqtt.MQTT_LOG_WARNING:
            self.logger.warning(f"MQTT Warning: {buf}")
        elif level == mqtt.MQTT_LOG_INFO:
            self.logger.info(f"MQTT Info: {buf}")
        elif level == mqtt.MQTT_LOG_DEBUG:
            self.logger.debug(f"MQTT Debug: {buf}")
    
    def start(self):
        """Iniciar cliente MQTT."""
        try:
            # Configurar SSL
            if self.config['MQTT_USE_SSL']:
                self.setup_ssl()
            
            # Configurar autenticación
            self.client.username_pw_set(
                self.config['MQTT_USERNAME'],
                self.config['MQTT_PASSWORD']
            )
            
            # Configurar callbacks
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            self.client.on_log = self.on_log
            
            # Conectar al broker
            self.logger.info(f"Conectando a {self.config['MQTT_BROKER_HOST']}:{self.config['MQTT_BROKER_PORT']}")
            self.client.connect(
                self.config['MQTT_BROKER_HOST'],
                self.config['MQTT_BROKER_PORT'],
                60
            )
            
            # Iniciar loop en hilo separado
            self.client.loop_start()
            
        except Exception as e:
            self.logger.error(f"Error iniciando cliente MQTT: {e}")
            raise
    
    def stop(self):
        """Detener cliente MQTT."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            self.logger.info("Cliente MQTT detenido")
        except Exception as e:
            self.logger.error(f"Error deteniendo cliente MQTT: {e}")
    
    def publish_command(self, topic, command):
        """
        Publicar comando a un tópico.
        
        Args:
            topic: Tópico donde publicar
            command: Comando a enviar
            
        Returns:
            bool: True si se envió exitosamente, False en caso contrario
        """
        try:
            if self.is_connected:
                self.client.publish(topic, command, qos=1)
                self.logger.info(f"Comando enviado a {topic}: {command}")
                return True
            else:
                self.logger.error("Cliente MQTT no conectado")
                return False
        except Exception as e:
            self.logger.error(f"Error enviando comando: {e}")
            return False
    
    def get_connection_status(self):
        """
        Obtener estado de conexión.
        
        Returns:
            dict: Información del estado de conexión
        """
        return {
            "connected": self.is_connected,
            "broker": self.config['MQTT_BROKER_HOST'],
            "client_id": self.config['MQTT_CLIENT_ID'],
            "reconnect_attempts": self.reconnect_attempts
        } 