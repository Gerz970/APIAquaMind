# Se crea la clase para manejar las configuraciones
from typing import Optional, List
from utils.connectiondb import get_session
from models.configuraciones import TbConfiguracion


class ConfiguracionCRUD:
    def __init__(self):
        pass

    def crear_configuracion(self, configuracion_data: dict) -> dict:
        """
        Crea una nueva configuración si no existe una con el mismo nombre de configuración.
        Devuelve la nueva configuración o None si ya existe.
        """
        session = get_session()
        try:
            # Verificar si ya existe una configuración con el mismo nombre
            configuracion_existente = session.query(TbConfiguracion).filter(
                TbConfiguracion.configuracion == configuracion_data['configuracion']
            ).first()
            
            if configuracion_existente:
                return {"message": "Ya existe una configuración con ese nombre"}, 409
            
            nueva_configuracion = TbConfiguracion(**configuracion_data)
            session.add(nueva_configuracion)
            session.commit()
            return nueva_configuracion.to_dict(), 200
        except Exception as e:
            session.rollback()
            return {"message": "Error al crear la configuración", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_todas(self) -> dict:
        """
        Obtiene todas las configuraciones.
        """
        session = get_session()
        try:
            configuraciones = session.query(TbConfiguracion).all()
            return [config.to_dict() for config in configuraciones], 200
        except Exception as e:
            return {"message": "Error al obtener las configuraciones", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_por_configuracion(self, configuracion: str) -> dict:
        """
        Obtiene una configuración por su nombre de configuración.
        """
        session = get_session()
        try:
            config_obj = session.query(TbConfiguracion).filter(
                TbConfiguracion.configuracion == configuracion
            ).first()
            
            if not config_obj:
                return {"message": "Configuración no encontrada"}, 404
            
            return config_obj.to_dict(), 200
        except Exception as e:
            return {"message": "Error al obtener la configuración", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_por_id(self, id_configuracion: int) -> dict:
        """
        Obtiene una configuración por su ID.
        """
        session = get_session()
        try:
            config_obj = session.query(TbConfiguracion).filter(
                TbConfiguracion.id_configuracion == id_configuracion
            ).first()
            
            if not config_obj:
                return {"message": "Configuración no encontrada"}, 404
            
            return config_obj.to_dict(), 200
        except Exception as e:
            return {"message": "Error al obtener la configuración", "error": str(e)}, 500
        finally:
            session.close()
    
    def actualizar_configuracion(self, configuracion: str, campos_actualizados: dict) -> dict:
        """
        Actualiza una configuración por su nombre de configuración.
        """
        session = get_session()
        try:
            config_obj = session.query(TbConfiguracion).filter(
                TbConfiguracion.configuracion == configuracion
            ).first()
            
            if not config_obj:
                return {"message": "Configuración no encontrada"}, 404
            
            # Actualizar los campos del objeto
            for key, value in campos_actualizados.items():
                if hasattr(config_obj, key) and key != 'configuracion':  # No permitir cambiar el nombre de configuración
                    setattr(config_obj, key, value)
                elif key == 'configuracion':
                    return {"message": "No se puede cambiar el nombre de la configuración"}, 400
            
            session.commit()
            return config_obj.to_dict(), 200
        except Exception as e:
            session.rollback()
            return {"message": "Error al actualizar la configuración", "error": str(e)}, 500
        finally:
            session.close()
    
    def actualizar_por_id(self, id_configuracion: int, campos_actualizados: dict) -> dict:
        """
        Actualiza una configuración por su ID.
        """
        session = get_session()
        try:
            config_obj = session.query(TbConfiguracion).filter(
                TbConfiguracion.id_configuracion == id_configuracion
            ).first()
            
            if not config_obj:
                return {"message": "Configuración no encontrada"}, 404
            
            # Actualizar los campos del objeto
            for key, value in campos_actualizados.items():
                if hasattr(config_obj, key) and key != 'configuracion':  # No permitir cambiar el nombre de configuración
                    setattr(config_obj, key, value)
                elif key == 'configuracion':
                    return {"message": "No se puede cambiar el nombre de la configuración"}, 400
            
            session.commit()
            return config_obj.to_dict(), 200
        except Exception as e:
            session.rollback()
            return {"message": "Error al actualizar la configuración", "error": str(e)}, 500
        finally:
            session.close()
    
    def eliminar_configuracion(self, configuracion: str) -> dict:
        """
        Elimina una configuración por su nombre de configuración.
        """
        session = get_session()
        try:
            config_obj = session.query(TbConfiguracion).filter(
                TbConfiguracion.configuracion == configuracion
            ).first()
            
            if not config_obj:
                return {"message": "Configuración no encontrada"}, 404
            
            session.delete(config_obj)
            session.commit()
            return {"message": "Configuración eliminada correctamente"}, 200
        except Exception as e:
            session.rollback()
            return {"message": "Error al eliminar la configuración", "error": str(e)}, 500
        finally:
            session.close()
    
    def eliminar_por_id(self, id_configuracion: int) -> dict:
        """
        Elimina una configuración por su ID.
        """
        session = get_session()
        try:
            config_obj = session.query(TbConfiguracion).filter(
                TbConfiguracion.id_configuracion == id_configuracion
            ).first()
            
            if not config_obj:
                return {"message": "Configuración no encontrada"}, 404
            
            session.delete(config_obj)
            session.commit()
            return {"message": "Configuración eliminada correctamente"}, 200
        except Exception as e:
            session.rollback()
            return {"message": "Error al eliminar la configuración", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_por_estatus(self, id_estatus: int) -> dict:
        """
        Obtiene todas las configuraciones por estatus.
        """
        session = get_session()
        try:
            configuraciones = session.query(TbConfiguracion).filter(
                TbConfiguracion.id_estatus == id_estatus
            ).all()
            
            return [config.to_dict() for config in configuraciones], 200
        except Exception as e:
            return {"message": "Error al obtener las configuraciones", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_valor_configuracion(self, configuracion: str) -> dict:
        """
        Obtiene solo el valor de una configuración específica.
        """
        session = get_session()
        try:
            config_obj = session.query(TbConfiguracion).filter(
                TbConfiguracion.configuracion == configuracion
            ).first()
            
            if not config_obj:
                return {"message": "Configuración no encontrada"}, 404
            
            return {"configuracion": config_obj.configuracion, "valor": config_obj.valor}, 200
        except Exception as e:
            return {"message": "Error al obtener el valor de la configuración", "error": str(e)}, 500
        finally:
            session.close() 