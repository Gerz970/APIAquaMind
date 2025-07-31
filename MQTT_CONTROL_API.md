# API de Control MQTT Centralizado

## Endpoint Principal

### `POST /mqtt/control`

Controla dispositivos individual o masivamente desde un solo endpoint.

---

## Comandos Individuales

### Request
```json
{
    "device": "valve1|valve2|gate|relay1|relay2",
    "command": "ON|OFF|OPEN|CLOSE"
}
```

### Ejemplos

#### Abrir Válvula 1
```json
{
    "device": "valve1",
    "command": "ON"
}
```

#### Cerrar Compuerta
```json
{
    "device": "gate",
    "command": "CLOSE"
}
```

#### Activar Relevador B2
```json
{
    "device": "relay2",
    "command": "ON"
}
```

### Response (Individual)
```json
{
    "success": true,
    "message": "Comando enviado exitosamente",
    "data": {
        "device": "valve1",
        "command": "ON",
        "topic": "control/valvula1",
        "description": "Válvula 1",
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

---

## Comandos Masivos

### Request
```json
{
    "devices": [
        {
            "device": "valve1",
            "command": "ON"
        },
        {
            "device": "valve2",
            "command": "OFF"
        },
        {
            "device": "gate",
            "command": "CLOSE"
        },
        {
            "device": "relay1",
            "command": "ON"
        },
        {
            "device": "relay2",
            "command": "OFF"
        }
    ]
}
```

### Response (Masivo)
```json
{
    "success": true,
    "message": "Comandos procesados",
    "data": {
        "total_commands": 5,
        "successful": 4,
        "failed": 1,
        "results": [
            {
                "device": "valve1",
                "command": "ON",
                "status": "success",
                "topic": "control/valvula1",
                "description": "Válvula 1"
            },
            {
                "device": "valve2",
                "command": "OFF",
                "status": "success",
                "topic": "control/valvula2",
                "description": "Válvula 2"
            },
            {
                "device": "gate",
                "command": "CLOSE",
                "status": "success",
                "topic": "control/compuerta",
                "description": "Compuerta"
            },
            {
                "device": "relay1",
                "command": "ON",
                "status": "success",
                "topic": "control/releb1",
                "description": "Relevador B1"
            },
            {
                "device": "relay2",
                "command": "OFF",
                "status": "error",
                "error": "Error enviando comando"
            }
        ]
    }
}
```

---

## Dispositivos Disponibles

### `GET /mqtt/devices`

Obtiene información de todos los dispositivos disponibles.

### Response
```json
{
    "success": true,
    "devices": [
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
            "commands": ["OPEN", "CLOSE"],
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
}
```

---

## Mapeo de Dispositivos

| Dispositivo | ID | Tópico | Comandos | Descripción |
|-------------|----|--------|----------|-------------|
| Válvula 1 | `valve1` | `control/valvula1` | `ON`, `OFF` | Abre o cierra válvula 1 |
| Válvula 2 | `valve2` | `control/valvula2` | `ON`, `OFF` | Abre o cierra válvula 2 |
| Compuerta | `gate` | `control/compuerta` | `OPEN`, `CLOSE` | Abre o cierra compuerta |
| Relevador B1 | `relay1` | `control/releb1` | `ON`, `OFF` | Activa o desactiva rele B1 |
| Relevador B2 | `relay2` | `control/releb2` | `ON`, `OFF` | Activa o desactiva rele B2 |

---

## Casos de Uso

### 1. Control Individual
- Control manual desde interfaz de usuario
- Comandos de emergencia
- Testing individual de dispositivos

### 2. Control Masivo
- Secuencias de comandos
- Configuraciones iniciales del sistema
- Operaciones de mantenimiento
- Escenarios automatizados

### 3. Ejemplos de Secuencias

#### Inicio del Sistema
```json
{
    "devices": [
        {"device": "valve1", "command": "OFF"},
        {"device": "valve2", "command": "OFF"},
        {"device": "gate", "command": "CLOSE"},
        {"device": "relay1", "command": "OFF"},
        {"device": "relay2", "command": "OFF"}
    ]
}
```

#### Parada de Emergencia
```json
{
    "devices": [
        {"device": "valve1", "command": "OFF"},
        {"device": "valve2", "command": "OFF"},
        {"device": "gate", "command": "CLOSE"},
        {"device": "relay1", "command": "OFF"},
        {"device": "relay2", "command": "OFF"}
    ]
}
```

#### Configuración de Riego
```json
{
    "devices": [
        {"device": "valve1", "command": "ON"},
        {"device": "gate", "command": "OPEN"},
        {"device": "relay1", "command": "ON"}
    ]
}
```

---

## Códigos de Error

### 400 - Bad Request
- Datos JSON requeridos
- Formato inválido
- Campos requeridos faltantes
- Dispositivo no válido
- Comando no válido para el dispositivo

### 401 - Unauthorized
- Token JWT requerido
- Token inválido o expirado

### 500 - Internal Server Error
- Error interno del servidor
- Cliente MQTT no conectado
- Error enviando comando

---

## Autenticación

Todos los endpoints requieren autenticación JWT. Incluye el token en el header:

```
Authorization: Bearer <tu_token_jwt>
```

---

## Ventajas del Sistema Centralizado

✅ **Un solo endpoint** para todos los comandos
✅ **Flexibilidad** entre individual y masivo
✅ **Validación centralizada** de dispositivos y comandos
✅ **Respuestas consistentes** y detalladas
✅ **Logging unificado** de todas las operaciones
✅ **Fácil mantenimiento** y escalabilidad
✅ **Compatibilidad** con endpoints existentes 