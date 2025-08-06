#!/usr/bin/env python3
"""
Script de prueba para el CRUD de niveles de agua.

Este script demuestra todas las operaciones CRUD disponibles
para la tabla tb_niveles_agua.
"""

import requests
import json
from datetime import datetime, timedelta

def test_niveles_agua_crud():
    """
    Probar todas las operaciones CRUD de niveles de agua.
    """
    base_url = "http://localhost:5000/api/v1"
    
    print("🧪 Iniciando prueba del CRUD de niveles de agua...")
    print("=" * 60)
    
    # 1. Crear un nuevo nivel de agua
    print("1. Creando nuevo nivel de agua...")
    nuevo_nivel = {
        "distancia": 15.5,
        "desnivel": "False",
        "bomba": "False",
        "compuerta": "False",
        "nivel_estado": "NORMAL",
        "porcentaje_agua": 65.0,
        "fecha": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(f"{base_url}/niveles-agua", json=nuevo_nivel)
        result = response.json()
        print(f"   Resultado: {result}")
        
        if result.get('success'):
            nivel_id = result['data']['id_nivel']
            print(f"   ID del nivel creado: {nivel_id}")
        else:
            print("   Error creando nivel de agua")
            return
            
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # 2. Obtener el nivel creado
    print(f"\n2. Obteniendo nivel de agua con ID {nivel_id}...")
    try:
        response = requests.get(f"{base_url}/niveles-agua/{nivel_id}")
        result = response.json()
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Obtener todos los niveles
    print("\n3. Obteniendo todos los niveles de agua...")
    try:
        response = requests.get(f"{base_url}/niveles-agua?limit=5")
        result = response.json()
        print(f"   Total de registros: {result.get('total', 0)}")
        print(f"   Registros obtenidos: {len(result.get('data', []))}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Actualizar el nivel
    print(f"\n4. Actualizando nivel de agua con ID {nivel_id}...")
    datos_actualizacion = {
        "distancia": 12.8,
        "nivel_estado": "ALTO",
        "porcentaje_agua": 75.0
    }
    
    try:
        response = requests.put(f"{base_url}/niveles-agua/{nivel_id}", json=datos_actualizacion)
        result = response.json()
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 5. Obtener el último nivel
    print("\n5. Obteniendo el último nivel de agua...")
    try:
        response = requests.get(f"{base_url}/niveles-agua/ultimo")
        result = response.json()
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 6. Obtener estadísticas
    print("\n6. Obteniendo estadísticas de niveles de agua...")
    try:
        response = requests.get(f"{base_url}/niveles-agua/estadisticas?dias=7")
        result = response.json()
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 7. Obtener niveles por fecha
    print("\n7. Obteniendo niveles por rango de fechas...")
    fecha_inicio = (datetime.now() - timedelta(days=1)).isoformat()
    fecha_fin = datetime.now().isoformat()
    
    try:
        response = requests.get(f"{base_url}/niveles-agua/por-fecha?fecha_inicio={fecha_inicio}&fecha_fin={fecha_fin}")
        result = response.json()
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 8. Eliminar el nivel creado
    print(f"\n8. Eliminando nivel de agua con ID {nivel_id}...")
    try:
        response = requests.delete(f"{base_url}/niveles-agua/{nivel_id}")
        result = response.json()
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Prueba del CRUD completada!")
    print("\n📋 Endpoints disponibles:")
    print("   POST   /niveles-agua                    - Crear nivel de agua")
    print("   GET    /niveles-agua                    - Obtener todos (con paginación)")
    print("   GET    /niveles-agua/{id}              - Obtener por ID")
    print("   PUT    /niveles-agua/{id}              - Actualizar por ID")
    print("   DELETE /niveles-agua/{id}              - Eliminar por ID")
    print("   GET    /niveles-agua/ultimo            - Obtener último registro")
    print("   GET    /niveles-agua/estadisticas      - Obtener estadísticas")
    print("   GET    /niveles-agua/por-fecha         - Obtener por rango de fechas")

if __name__ == "__main__":
    test_niveles_agua_crud() 