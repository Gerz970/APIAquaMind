#!/usr/bin/env python3
"""
Script para corregir las contraseñas hasheadas en la base de datos.

Este script soluciona el problema de "Invalid hash method" regenerando
todas las contraseñas en la base de datos usando bcrypt de manera consistente.
"""

import os
import sys
import bcrypt
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importar después de configurar el path
try:
    from app.database import get_db_session, close_db_session
    from app.models.seguridad import TbUsuario
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Asegúrate de estar en el directorio correcto y tener todas las dependencias instaladas")
    sys.exit(1)

def fix_password_hashes():
    """
    Corregir todas las contraseñas hasheadas en la base de datos.
    """
    print("🔧 Corrigiendo hashes de contraseñas...")
    
    try:
        session = get_db_session()
        
        # Obtener todos los usuarios
        usuarios = session.query(TbUsuario).all()
        
        if not usuarios:
            print("ℹ️ No hay usuarios en la base de datos")
            return True
        
        print(f"📝 Encontrados {len(usuarios)} usuarios para corregir")
        
        # Contraseña por defecto para regenerar
        default_password = "Admin123!"
        
        for i, usuario in enumerate(usuarios, 1):
            try:
                # Regenerar el hash de la contraseña usando bcrypt
                new_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Actualizar la contraseña en la base de datos
                usuario._password = new_hash
                
                print(f"✅ Usuario {i}/{len(usuarios)}: {usuario.username} - Hash corregido")
                
            except Exception as e:
                print(f"❌ Error al corregir usuario {usuario.username}: {e}")
                continue
        
        # Guardar todos los cambios
        session.commit()
        print(f"💾 Cambios guardados en la base de datos")
        
        print("\n📋 Resumen:")
        print(f"   - Usuarios procesados: {len(usuarios)}")
        print(f"   - Contraseña por defecto: {default_password}")
        print(f"   - Método de hash: bcrypt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al corregir hashes: {e}")
        return False
    finally:
        close_db_session(session)

def verify_fix():
    """
    Verificar que las contraseñas se corrigieron correctamente.
    """
    print("\n🔍 Verificando corrección...")
    
    try:
        session = get_db_session()
        
        # Buscar el usuario admin
        usuario = session.query(TbUsuario).filter_by(username="admin").first()
        
        if not usuario:
            print("❌ Usuario admin no encontrado")
            return False
        
        # Intentar verificar la contraseña
        test_password = "Admin123!"
        if usuario.verify_password(test_password):
            print("✅ Verificación exitosa - El hash funciona correctamente")
            return True
        else:
            print("❌ Verificación fallida - El hash aún no funciona")
            return False
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False
    finally:
        close_db_session(session)

def main():
    """Función principal."""
    print("🚀 Corrección de Hashes de Contraseñas - APIAquaMind")
    print("=" * 60)
    
    # 1. Corregir hashes
    if not fix_password_hashes():
        print("\n❌ No se pudieron corregir los hashes.")
        return
    
    # 2. Verificar corrección
    if not verify_fix():
        print("\n❌ La corrección no funcionó correctamente.")
        return
    
    print("\n🎉 Corrección completada exitosamente!")
    print("\n📝 Información importante:")
    print("   - Todas las contraseñas fueron reseteadas a: Admin123!")
    print("   - Los hashes ahora usan bcrypt de manera consistente")
    print("   - El error 'Invalid hash method' debería estar resuelto")
    print("\n🔐 Próximos pasos:")
    print("   1. Probar login con: admin / Admin123!")
    print("   2. Cambiar contraseñas por seguridad")
    print("   3. Ejecutar la aplicación: python start.py")

if __name__ == '__main__':
    main() 