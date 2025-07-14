#!/usr/bin/env python3
"""
Script de ejecución para APIAquaMind.

Este script configura el PYTHONPATH correctamente y ejecuta la aplicación.
Es útil para evitar problemas de importación de módulos.
"""

import sys
import os

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar la aplicación
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host="0.0.0.0", 
        port=5000, 
        debug=app.config.get('DEBUG', False)
    ) 