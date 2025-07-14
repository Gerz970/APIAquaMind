"""
Punto de entrada principal de la aplicación APIAquaMind.

Este archivo es el punto de entrada para ejecutar la aplicación Flask.
Utiliza el patrón Application Factory para crear la instancia de la aplicación
con la configuración apropiada según el entorno.

Características:
- Usa el patrón Factory para crear la app
- Configuración automática según entorno
- Ejecución local para desarrollo
- Preparado para despliegue con Gunicorn
"""

import sys
import os

# Agregar el directorio padre al PYTHONPATH para poder importar app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Importar create_app
from app import create_app

# Crear la instancia de la aplicación usando el patrón Factory
# Esto permite crear la app con diferentes configuraciones según el entorno
app = create_app()

# Bloque de ejecución principal
# Este código solo se ejecuta cuando el archivo se ejecuta directamente
# (no cuando se importa como módulo)
if __name__ == '__main__':
    # Ejecutar la aplicación en modo desarrollo
    # host="0.0.0.0" permite conexiones desde cualquier IP
    # port=5000 es el puerto por defecto de Flask
    # debug se obtiene de la configuración de la app
    app.run(
        host="0.0.0.0", 
        port=5000, 
        debug=app.config.get('DEBUG', False)
    )
