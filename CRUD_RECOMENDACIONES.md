# CRUD de Recomendaciones - APIAquaMind

## Descripción General

El sistema de recomendaciones de APIAquaMind permite gestionar recomendaciones personalizadas para los usuarios. Cada recomendación incluye un nombre, descripción, imagen e icono, y puede ser activada o desactivada mediante baja lógica.

## Estructura del Modelo

### TbRecomendacion

```python
class TbRecomendacion(Base):
    __tablename__ = 'tb_recomendaciones'
    
    id_recomendacion = Column(Integer, primary_key=True, autoincrement=True)
    recomendacion = Column(Text, nullable=False)        # Nombre de la recomendación
    descripcion = Column(Text, nullable=False)          # Descripción detallada
    url_imagen = Column(String(255), nullable=False)    # URL de la imagen
    icono = Column(String(255), nullable=False)         # Icono (emoji o texto)
    id_estatus = Column(Integer, nullable=False, default=1)  # 1=activo, 0=inactivo
```

## Endpoints Disponibles

### 1. Listar Recomendaciones
**GET** `/api/v1/recomendaciones/listar`

Obtiene todas las recomendaciones activas del sistema.

**Respuesta:**
```json
[
  {
    "id_recomendacion": 1,
    "recomendacion": "Beber más agua",
    "descripcion": "Se recomienda beber al menos 8 vasos de agua al día",
    "url_imagen": "https://ejemplo.com/agua.jpg",
    "icono": "💧",
    "id_estatus": 1
  }
]
```

### 2. Obtener Recomendaciones Aleatorias
**GET** `/api/v1/recomendaciones/aleatorias/{cantidad}`

Obtiene una cantidad específica de recomendaciones aleatorias activas.

**Parámetros:**
- `cantidad` (int): Número de recomendaciones a obtener

**Ejemplo:** `/api/v1/recomendaciones/aleatorias/5`

### 3. Crear Recomendación
**POST** `/api/v1/recomendaciones/recomendacion`

Crea una nueva recomendación en el sistema.

**Body:**
```json
{
  "recomendacion": "Beber más agua",
  "descripcion": "Se recomienda beber al menos 8 vasos de agua al día",
  "url_imagen": "https://ejemplo.com/agua.jpg",
  "icono": "💧"
}
```

**Respuesta exitosa (200):**
```json
{
  "id_recomendacion": 1,
  "recomendacion": "Beber más agua",
  "descripcion": "Se recomienda beber al menos 8 vasos de agua al día",
  "url_imagen": "https://ejemplo.com/agua.jpg",
  "icono": "💧",
  "id_estatus": 1
}
```

**Respuesta de error (400):**
```json
{
  "message": "Ya existe una recomendación con ese nombre",
  "key": "recomendacion"
}
```

### 4. Actualizar Recomendación
**PUT** `/api/v1/recomendaciones/recomendacion/{id_recomendacion}`

Actualiza una recomendación existente.

**Parámetros:**
- `id_recomendacion` (int): ID de la recomendación a actualizar

**Body:**
```json
{
  "recomendacion": "Beber más agua diariamente",
  "descripcion": "Se recomienda beber al menos 2 litros de agua al día",
  "url_imagen": "https://ejemplo.com/nueva-imagen.jpg",
  "icono": "🚰"
}
```

### 5. Eliminar Recomendación (Baja Lógica)
**DELETE** `/api/v1/recomendaciones/recomendacion/{id_recomendacion}`

Realiza una baja lógica de la recomendación (cambia `id_estatus` a 0).

**Parámetros:**
- `id_recomendacion` (int): ID de la recomendación a eliminar

**Respuesta (200):**
```json
true
```

### 6. Reactivar Recomendación
**PUT** `/api/v1/recomendaciones/recomendacion/{id_recomendacion}/reactivar`

Reactiva una recomendación previamente dada de baja.

**Parámetros:**
- `id_recomendacion` (int): ID de la recomendación a reactivar

### 7. Obtener Recomendación por ID
**GET** `/api/v1/recomendaciones/recomendacion/{id_recomendacion}`

Obtiene la información detallada de una recomendación específica.

**Parámetros:**
- `id_recomendacion` (int): ID de la recomendación a obtener

## Clase RecomendacionesCRUD

### Métodos Disponibles

#### `crear_recomendacion(recomendacion_data: dict) -> tuple`
- Crea una nueva recomendación
- Verifica que no exista una con el mismo nombre
- Retorna: `(datos_recomendacion, status_code)`

#### `actualizar_recomendacion(id_recomendacion: int, recomendacion_data: dict) -> tuple`
- Actualiza una recomendación existente
- Solo actualiza campos válidos
- Retorna: `(datos_recomendacion, status_code)`

#### `eliminar_recomendacion(id_recomendacion: int) -> tuple`
- Realiza baja lógica (id_estatus = 0)
- Retorna: `(True/False, status_code)`

#### `reactivar_recomendacion(id_recomendacion: int) -> tuple`
- Reactiva una recomendación inactiva
- Retorna: `(datos_recomendacion, status_code)`

#### `obtener_por_id(id_recomendacion: int) -> dict`
- Obtiene recomendación por ID
- Solo retorna recomendaciones activas
- Retorna: `dict` o `None`

#### `obtener_por_nombre(nombre: str) -> dict`
- Obtiene recomendación por nombre
- Solo retorna recomendaciones activas
- Retorna: `dict` o `None`

#### `obtener_todas() -> List[dict]`
- Obtiene todas las recomendaciones activas
- Retorna: `List[dict]`

#### `obtener_recomendaciones_aleatorias(cantidad: int) -> List[dict]`
- Obtiene recomendaciones aleatorias activas
- Retorna: `List[dict]`

## Características del Sistema

### ✅ Baja Lógica
- Las recomendaciones no se eliminan físicamente
- Se marcan como inactivas (`id_estatus = 0`)
- Pueden ser reactivadas posteriormente

### ✅ Validaciones
- Verificación de duplicados por nombre
- Solo permite actualizar campos válidos del modelo
- Manejo de errores consistente con códigos de estado HTTP

### ✅ Gestión de Sesiones
- Uso correcto de sesiones de base de datos
- Cierre automático de sesiones para evitar fugas de memoria
- Patrón consistente con otros CRUDs del sistema

### ✅ Documentación Swagger
- Todos los endpoints incluyen documentación completa
- Ejemplos de uso y respuestas
- Esquemas de datos detallados

## Ejemplos de Uso

### Crear una nueva recomendación
```python
from core.recomendaciones import RecomendacionesCRUD

crud = RecomendacionesCRUD()
datos = {
    "recomendacion": "Hacer ejercicio",
    "descripcion": "Realizar al menos 30 minutos de actividad física diaria",
    "url_imagen": "https://ejemplo.com/ejercicio.jpg",
    "icono": "🏃‍♂️"
}

resultado, status = crud.crear_recomendacion(datos)
```

### Obtener recomendaciones aleatorias
```python
recomendaciones = crud.obtener_recomendaciones_aleatorias(3)
```

### Actualizar una recomendación
```python
datos_actualizados = {
    "descripcion": "Realizar al menos 45 minutos de actividad física diaria"
}
resultado, status = crud.actualizar_recomendacion(1, datos_actualizados)
```

## Integración con el Sistema

El CRUD de recomendaciones está completamente integrado con:

- **Sistema de rutas**: Blueprint registrado en `/api/v1/recomendaciones/`
- **Documentación Swagger**: Disponible en `/apidocs`
- **Manejo de errores**: Respuestas consistentes con el resto de la API
- **Configuración**: Usa la misma configuración de base de datos que otros módulos

## Notas de Implementación

1. **Consistencia**: Sigue el mismo patrón que el CRUD de usuarios
2. **Seguridad**: Incluye validaciones y manejo de errores
3. **Escalabilidad**: Preparado para futuras funcionalidades
4. **Mantenibilidad**: Código bien documentado y estructurado 