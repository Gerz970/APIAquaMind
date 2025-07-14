#!/usr/bin/env python3
"""
Script para configurar el entorno de desarrollo de APIAquaMind.

Este script configura el PYTHONPATH y las variables de entorno necesarias
para ejecutar la aplicación correctamente.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Configurar el entorno de desarrollo."""
    
    # Obtener el directorio raíz del proyecto
    project_root = Path(__file__).parent.absolute()
    
    # Agregar el directorio raíz al PYTHONPATH
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Configurar variables de entorno por defecto si no existen
    env_vars = {
        'FLASK_ENV': 'development',
        'DEBUG': 'True',
        'PORT': '5000',
        'API_PREFIX': '/api/v1',
        'LOG_LEVEL': 'DEBUG'
    }
    
    for key, value in env_vars.items():
        if not os.getenv(key):
            os.environ[key] = value
    
    print(f"✅ Entorno configurado correctamente")
    print(f"📁 Directorio raíz: {project_root}")
    print(f"🐍 PYTHONPATH: {sys.path[0]}")
    print(f"🔧 Variables de entorno configuradas: {list(env_vars.keys())}")

if __name__ == '__main__':
    setup_environment()
    
    # Importar y ejecutar la aplicación
    try:
        from app import create_app
        
        app = create_app()
        
        print(f"🚀 Iniciando aplicación en modo desarrollo...")
        print(f"🌐 URL: http://localhost:{app.config.get('PORT', 5000)}")
        print(f"📚 API Docs: http://localhost:{app.config.get('PORT', 5000)}/apidocs")
        
        app.run(
            host="0.0.0.0", 
            port=app.config.get('PORT', 5000), 
            debug=app.config.get('DEBUG', False)
        )
        
    except ImportError as e:
        print(f"❌ Error al importar la aplicación: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        sys.exit(1) 