#!/usr/bin/env python3
"""
Script para configurar y verificar la conexión a la base de datos.

Este script te ayuda a:
1. Verificar la conexión a tu base de datos
2. Crear las tablas necesarias
3. Insertar datos de prueba
4. Validar la configuración
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import get_db_session, close_db_session
from app.models.seguridad import TbUsuario, Base
from app.database import db_manager
# Removido werkzeug.security import - usando bcrypt directamente
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Probar la conexión a la base de datos."""
    print("🔍 Probando conexión a la base de datos...")
    
    try:
        session = get_db_session()
        
        # Intentar una consulta simple
        result = session.execute("SELECT 1 as test")
        test_value = result.fetchone()[0]
        
        if test_value == 1:
            print("✅ Conexión a la base de datos exitosa")
            return True
        else:
            print("❌ Error en la consulta de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    finally:
        close_db_session(session)

def create_tables():
    """Crear las tablas necesarias en la base de datos."""
    print("🏗️ Creando tablas en la base de datos...")
    
    try:
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(db_manager.engine)
        print("✅ Tablas creadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        return False

def insert_test_data():
    """Insertar datos de prueba en la base de datos."""
    print("📝 Insertando datos de prueba...")
    
    try:
        session = get_db_session()
        
        # Verificar si ya existe un usuario de prueba
        existing_user = session.query(TbUsuario).filter_by(username="admin").first()
        
        if existing_user:
            print("ℹ️ Usuario de prueba ya existe")
            return True
        
        # Crear usuario de prueba
        test_user = TbUsuario(
            username="admin",
            password="Admin123!",  # Se hasheará automáticamente
            correo_electronico="admin@aquamind.com",
            nombre="Administrador",
            apellido_paterno="Sistema",
            id_tipo_usuario=1,
            id_estatus=1
        )
        
        session.add(test_user)
        session.commit()
        
        print("✅ Usuario de prueba creado:")
        print(f"   Usuario: admin")
        print(f"   Contraseña: Admin123!")
        print(f"   Email: admin@aquamind.com")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al insertar datos de prueba: {e}")
        return False
    finally:
        close_db_session(session)

def validate_configuration():
    """Validar la configuración actual."""
    print("🔧 Validando configuración...")
    
    # Verificar variables de entorno requeridas
    required_vars = ['SERVER', 'DATABASE', 'USER', 'PASSWORD', 'JWT_SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("💡 Asegúrate de tener un archivo .env configurado")
        return False
    
    print("✅ Todas las variables de entorno están configuradas")
    
    # Mostrar configuración (sin contraseñas)
    print("\n📋 Configuración actual:")
    print(f"   Servidor: {os.getenv('SERVER')}")
    print(f"   Base de datos: {os.getenv('DATABASE')}")
    print(f"   Usuario: {os.getenv('USER')}")
    print(f"   Puerto: {os.getenv('PORT', '5000')}")
    print(f"   Entorno: {os.getenv('FLASK_ENV', 'development')}")
    
    return True

def main():
    """Función principal."""
    print("🚀 Configuración de Base de Datos APIAquaMind")
    print("=" * 50)
    
    # 1. Validar configuración
    if not validate_configuration():
        print("\n❌ Configuración inválida. Revisa tu archivo .env")
        return
    
    # 2. Probar conexión
    if not test_database_connection():
        print("\n❌ No se pudo conectar a la base de datos.")
        print("💡 Verifica:")
        print("   - Que el servidor esté activo")
        print("   - Que las credenciales sean correctas")
        print("   - Que el firewall permita la conexión")
        return
    
    # 3. Crear tablas
    if not create_tables():
        print("\n❌ No se pudieron crear las tablas.")
        return
    
    # 4. Insertar datos de prueba
    if not insert_test_data():
        print("\n❌ No se pudieron insertar los datos de prueba.")
        return
    
    print("\n🎉 Configuración completada exitosamente!")
    print("\n📝 Próximos pasos:")
    print("   1. Ejecutar la aplicación: python start.py")
    print("   2. Probar login con: admin / Admin123!")
    print("   3. Acceder a la documentación: http://localhost:5000/apidocs")

if __name__ == '__main__':
    main() 