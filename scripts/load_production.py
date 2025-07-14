#!/usr/bin/env python3
"""
Script para cargar configuración de producción.

Este script te ayuda a:
1. Cargar configuración de producción
2. Validar la configuración
3. Ejecutar la aplicación en modo producción
"""

import os
import sys
import shutil
from pathlib import Path

def load_production_config():
    """Cargar configuración de producción."""
    print("🚀 Cargando configuración de producción...")
    
    # Verificar si existe el archivo de producción
    production_env = Path("env.production")
    if not production_env.exists():
        print("❌ Archivo env.production no encontrado")
        print("💡 Crea el archivo env.production con tu configuración real")
        return False
    
    # Copiar configuración de producción a .env
    try:
        shutil.copy("env.production", ".env")
        print("✅ Configuración de producción cargada")
        return True
    except Exception as e:
        print(f"❌ Error al cargar configuración: {e}")
        return False

def validate_production_config():
    """Validar configuración de producción."""
    print("🔧 Validando configuración de producción...")
    
    # Verificar variables críticas
    critical_vars = {
        'FLASK_ENV': 'production',
        'DEBUG': 'False',
        'JWT_SECRET_KEY': 'tu-clave-secreta-super-segura-para-produccion-cambiar-por-una-clave-real',
        'SERVER': 'tu-servidor-sql-server.com',
        'DATABASE': 'tu-base-de-datos-real',
        'USER': 'tu-usuario-de-bd',
        'PASSWORD': 'tu-contraseña-de-bd'
    }
    
    warnings = []
    errors = []
    
    for var, default_value in critical_vars.items():
        current_value = os.getenv(var)
        
        if not current_value:
            errors.append(f"Variable {var} no está configurada")
        elif current_value == default_value:
            warnings.append(f"Variable {var} tiene valor por defecto (debe cambiarse)")
    
    if errors:
        print("❌ Errores encontrados:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    if warnings:
        print("⚠️ Advertencias:")
        for warning in warnings:
            print(f"   - {warning}")
        print("\n💡 Asegúrate de cambiar los valores por defecto antes de usar en producción")
    
    print("✅ Configuración de producción válida")
    return True

def show_production_info():
    """Mostrar información de la configuración de producción."""
    print("\n📋 Configuración de Producción Actual:")
    print("=" * 40)
    print(f"Entorno: {os.getenv('FLASK_ENV', 'N/A')}")
    print(f"Debug: {os.getenv('DEBUG', 'N/A')}")
    print(f"Puerto: {os.getenv('PORT', 'N/A')}")
    print(f"Servidor BD: {os.getenv('SERVER', 'N/A')}")
    print(f"Base de datos: {os.getenv('DATABASE', 'N/A')}")
    print(f"Usuario BD: {os.getenv('USER', 'N/A')}")
    print(f"Log Level: {os.getenv('LOG_LEVEL', 'N/A')}")

def main():
    """Función principal."""
    print("🏭 Cargador de Configuración de Producción APIAquaMind")
    print("=" * 60)
    
    # 1. Cargar configuración
    if not load_production_config():
        return
    
    # 2. Validar configuración
    if not validate_production_config():
        print("\n❌ Configuración inválida. Revisa tu archivo env.production")
        return
    
    # 3. Mostrar información
    show_production_info()
    
    # 4. Preguntar si ejecutar
    print("\n🤔 ¿Deseas ejecutar la aplicación en modo producción?")
    print("⚠️ ADVERTENCIA: Asegúrate de que la configuración sea correcta")
    
    response = input("¿Continuar? (y/N): ").lower().strip()
    
    if response in ['y', 'yes', 'sí', 'si']:
        print("\n🚀 Iniciando aplicación en modo producción...")
        
        # Importar y ejecutar la aplicación
        try:
            from app import create_app
            
            app = create_app()
            
            print(f"🌐 Servidor iniciado en http://localhost:{app.config.get('PORT', 5000)}")
            print("🔒 Modo producción activado")
            print("📝 Logs: Solo warnings y errores")
            
            app.run(
                host="0.0.0.0",
                port=app.config.get('PORT', 5000),
                debug=False
            )
            
        except Exception as e:
            print(f"❌ Error al iniciar la aplicación: {e}")
    else:
        print("✅ Configuración cargada. Ejecuta 'python start.py' cuando estés listo.")

if __name__ == '__main__':
    main() 