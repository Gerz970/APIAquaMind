# API de Nivel de Agua - APIAquaMind

## 📊 Descripción

Esta API permite obtener datos del sensor de nivel de agua conectado al sistema MQTT. El sensor proporciona información en tiempo real sobre el nivel de agua, estado de dispositivos y alertas de desnivel.

## 🔧 Configuración MQTT

El sistema está configurado para suscribirse al topic `sensor/nivelAgua` del broker MQTT de HiveMQ Cloud.

### Datos del Sensor

El ESP32 publica datos en formato JSON cada 5 segundos:

```json
{
  "distancia": 15.5,
  "desnivel": false,
  "bomba": false,
  "compuerta": false
}
```

### Interpretación de Datos

- **`distancia`**: Distancia en centímetros desde el sensor hasta la superficie del agua
- **`desnivel`**: Boolean que indica si hay desnivel detectado
- **`bomba`**: Estado de la bomba de drenaje
- **`compuerta`**: Estado de las compuertas de control

## 🚀 Endpoints Disponibles

### 1. Obtener Nivel de Agua Actual

**GET** `/api/v1/mqtt/water-level`

Obtiene los datos más recientes del sensor de nivel de agua.

#### Respuesta

```json
{
  "success": true,
  "data": {
    "distancia": 18.5,
    "desnivel": false,
    "bomba": false,
    "compuerta": false,
    "nivel_estado": "NORMAL",
    "timestamp": "2024-01-15T10:30:00"
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
  }
}
```

### 2. Obtener Historial de Nivel de Agua

**GET** `/api/v1/mqtt/water-level/history`

Obtiene el historial de datos del sensor de nivel de agua.

#### Parámetros de Consulta

- `days` (opcional): Número de días a consultar (1-365, por defecto 7)
- `limit` (opcional): Número máximo de registros (1-1000, por defecto 100)

#### Ejemplo de Uso

```
GET /api/v1/mqtt/water-level/history?days=7&limit=50
```

#### Respuesta

```json
{
  "success": true,
  "data": {
    "period": "7 días",
    "total_records": 50,
    "records": [
      {
        "distancia": 15.5,
        "desnivel": false,
        "bomba": false,
        "compuerta": false,
        "nivel_estado": "NORMAL",
        "timestamp": "2024-01-15T10:30:00"
      }
    ],
    "statistics": {
      "promedio_distancia": 16.2,
      "max_distancia": 25.0,
      "min_distancia": 8.5,
      "alertas_desnivel": 2,
      "activaciones_bomba": 5
    }
  }
}
```

## 📈 Estados del Nivel de Agua

### Clasificación por Distancia

| Estado | Distancia | Descripción | Color |
|--------|-----------|-------------|-------|
| CRÍTICO | - | Desnivel detectado | 🔴 Rojo |
| ALTO | ≤ 10 cm | Nivel muy alto | 🟠 Naranja |
| NORMAL | 10-20 cm | Nivel normal | 🟢 Verde |
| BAJO | 20-30 cm | Nivel bajo | 🟡 Amarillo |
| MUY_BAJO | > 30 cm | Nivel muy bajo | 🔴 Rojo |

### Interpretación de Estados

- **CRÍTICO**: Se ha detectado un desnivel. Requiere acción inmediata.
- **ALTO**: El nivel está por encima de lo normal. Considerar abrir compuertas.
- **NORMAL**: El nivel está dentro de los parámetros aceptables.
- **BAJO**: El nivel está por debajo de lo normal. Verificar suministro.
- **MUY_BAJO**: El nivel está muy por debajo de lo normal. Activar bombeo.

## 🔧 Configuración del Sistema

### Variables de Entorno MQTT

```bash
MQTT_BROKER_HOST=ae6dc87b8b334a3997065b77c26a0343.s1.eu.hivemq.cloud
MQTT_BROKER_PORT=8883
MQTT_USERNAME=AngelaGlz
MQTT_PASSWORD=4791384739An.
MQTT_CLIENT_ID=aquamind-api-client
MQTT_USE_SSL=True
```

### Topics MQTT

- **Entrada**: `sensor/nivelAgua` - Datos del sensor
- **Salida**: `control/compuerta` - Control de compuertas

## 🚨 Manejo de Errores

### Códigos de Estado

- **200**: Operación exitosa
- **400**: Parámetros inválidos
- **503**: Servicio MQTT no disponible
- **500**: Error interno del servidor

### Ejemplos de Errores

```json
{
  "success": false,
  "error": "MQTT está deshabilitado por configuración"
}
```

```json
{
  "success": false,
  "error": "El parámetro 'days' debe estar entre 1 y 365"
}
```

## 🔄 Integración con Base de Datos

Los datos del sensor se almacenan automáticamente en la base de datos como eventos del sistema, permitiendo:

- Historial completo de lecturas
- Análisis de tendencias
- Generación de reportes
- Alertas automáticas

## 📱 Ejemplos de Uso

### JavaScript (Fetch)

```javascript
// Obtener nivel actual
fetch('/api/v1/mqtt/water-level')
  .then(response => response.json())
  .then(data => {
    console.log('Nivel de agua:', data.data.distancia);
    console.log('Estado:', data.interpretacion.nivel);
  });

// Obtener historial
fetch('/api/v1/mqtt/water-level/history?days=7&limit=50')
  .then(response => response.json())
  .then(data => {
    console.log('Registros:', data.data.records.length);
    console.log('Promedio:', data.data.statistics.promedio_distancia);
  });
```

### Python (Requests)

```python
import requests

# Obtener nivel actual
response = requests.get('http://localhost:5000/api/v1/mqtt/water-level')
data = response.json()

if data['success']:
    print(f"Nivel: {data['data']['distancia']} cm")
    print(f"Estado: {data['interpretacion']['nivel']}")
else:
    print(f"Error: {data['error']}")
```

### cURL

```bash
# Obtener nivel actual
curl -X GET "http://localhost:5000/api/v1/mqtt/water-level"

# Obtener historial
curl -X GET "http://localhost:5000/api/v1/mqtt/water-level/history?days=7&limit=50"
```

## 🔍 Monitoreo y Alertas

El sistema proporciona:

- **Monitoreo en tiempo real** del nivel de agua
- **Alertas automáticas** cuando se detecta desnivel
- **Historial detallado** para análisis de tendencias
- **Estadísticas** de uso y activaciones
- **Recomendaciones** basadas en el estado actual

## 🛠️ Desarrollo

### Estructura de Archivos

```
app/
├── routes/
│   └── routes_mqtt.py          # Endpoints de nivel de agua
├── services/
│   ├── mqtt_client.py          # Cliente MQTT
│   └── mqtt_message_handler.py # Procesamiento de mensajes
└── core/
    └── mqtt_data_processor.py  # Almacenamiento de datos
```

### Próximas Mejoras

- [ ] Almacenamiento en cache para mejor rendimiento
- [ ] Alertas por email/SMS
- [ ] Gráficos en tiempo real
- [ ] Integración con sistemas de control automático
- [ ] API para control remoto de dispositivos 