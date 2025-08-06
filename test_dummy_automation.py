#!/usr/bin/env python3
"""
Script de prueba para la automatización del nivel de agua con datos dummy.

Este script simula el comportamiento del sistema cuando MQTT está apagado
y genera datos dummy automáticamente para probar la automatización.
"""

import requests
import time
import json
from datetime import datetime

def test_dummy_automation():
    """
    Probar la automatización con datos dummy.
    """
    base_url = "http://localhost:5000/api/v1"
    
    print("🧪 Iniciando prueba de automatización con datos dummy...")
    print("=" * 60)
    
    # 1. Verificar estado de MQTT
    print("1. Verificando estado de MQTT...")
    try:
        response = requests.get(f"{base_url}/mqtt/status")
        mqtt_status = response.json()
        print(f"   Estado MQTT: {mqtt_status}")
    except Exception as e:
        print(f"   Error verificando MQTT: {e}")
    
    print("\n2. Procesando datos dummy manualmente...")
    try:
        response = requests.post(f"{base_url}/mqtt/dummy/water-level")
        result = response.json()
        print(f"   Resultado: {result}")
    except Exception as e:
        print(f"   Error procesando datos dummy: {e}")
    
    print("\n3. Verificando datos del nivel de agua...")
    try:
        response = requests.get(f"{base_url}/mqtt/water-level")
        water_data = response.json()
        print(f"   Datos actuales: {json.dumps(water_data, indent=2)}")
    except Exception as e:
        print(f"   Error obteniendo datos: {e}")
    
    print("\n4. Verificando historial...")
    try:
        response = requests.get(f"{base_url}/mqtt/water-level/history?days=1&limit=5")
        history = response.json()
        print(f"   Registros en historial: {len(history.get('data', {}).get('records', []))}")
    except Exception as e:
        print(f"   Error obteniendo historial: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada!")
    print("\n📋 Información importante:")
    print("   - El sistema genera datos dummy cada 30 segundos cuando MQTT está apagado")
    print("   - Los datos incluyen diferentes escenarios: CRÍTICO, ALTO, NORMAL, BAJO, MUY_BAJO")
    print("   - Cuando se detecta desnivel (CRÍTICO), se activa automáticamente la compuerta")
    print("   - Cuando el nivel vuelve a NORMAL, se cierra automáticamente la compuerta")
    print("   - Todos los eventos se registran en la base de datos")
    print("\n🔍 Para monitorear en tiempo real:")
    print("   - Revisa los logs del servidor para ver la generación automática")
    print("   - Usa la API /mqtt/water-level para ver datos actuales")
    print("   - Usa la API /mqtt/water-level/history para ver el historial")

if __name__ == "__main__":
    test_dummy_automation() 