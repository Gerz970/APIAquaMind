#!/usr/bin/env python3
"""
Script de inicio robusto para APIAquaMind.

Este script maneja todos los casos de ejecución y configura el entorno
correctamente sin importar desde dónde se ejecute.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Configurar el entorno de desarrollo."""
    
    # Obtener el directorio raíz del proyecto
    script_path = Path(__file__).resolve()
    project_root = script_path.parent
    
    # Agregar el directorio raíz al PYTHONPATH
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Configurar variables de entorno por defecto
    default_env = {
        'FLASK_ENV': 'development',
        'DEBUG': 'True',
        'PORT': '5000',
        'API_PREFIX': '/api/v1',
        'LOG_LEVEL': 'DEBUG'
    }
    
    for key, value in default_env.items():
        if not os.getenv(key):
            os.environ[key] = value
    
    return project_root

def main():
    """Función principal."""
    
    print("🚀 Iniciando APIAquaMind...")
    
    try:
        # Configurar entorno
        project_root = setup_environment()
        print(f"✅ Entorno configurado")
        print(f"📁 Directorio raíz: {project_root}")
        
        # Importar la aplicación
        from app import create_app
        
        # Crear la aplicación
        app = create_app()
        
        # Obtener configuración
        port = app.config.get('PORT', 5000)
        debug = app.config.get('DEBUG', False)
        
        print(f"🌐 Iniciando servidor en http://localhost:{port}")
        print(f"📚 Documentación API: http://localhost:{port}/apidocs")
        print(f"🔧 Modo debug: {'Activado' if debug else 'Desactivado'}")
        print("=" * 50)
        
        # Ejecutar la aplicación
        app.run(
            host="0.0.0.0",
            port=port,
            debug=debug
        )
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Soluciones posibles:")
        print("   1. Instalar dependencias: pip install -r requirements.txt")
        print("   2. Verificar que estás en el directorio raíz del proyecto")
        print("   3. Activar el entorno virtual si lo tienes")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("💡 Verifica la configuración de la base de datos en .env")
        sys.exit(1)

if __name__ == '__main__':
    main() 