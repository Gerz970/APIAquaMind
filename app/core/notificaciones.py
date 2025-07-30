# Se crea la clase para manejar las notificaciones
from typing import Optional, List
from utils.connectiondb import get_session
from datetime import datetime
from models.notificaciones import TbNotificacion


class NotificacionCRUD:
    def __init__(self):
        pass

    def crear_notificacion(self, notificacion_data: dict) -> dict:
        """
        Crea una nueva notificación.
        Devuelve la nueva notificación o None si hay error.
        """
        session = get_session()
        try:
            # Si no se proporciona fecha, usar la fecha actual
            if 'fecha_notificacion' not in notificacion_data:
                notificacion_data['fecha_notificacion'] = datetime.now()
            
            nueva_notificacion = TbNotificacion(**notificacion_data)
            session.add(nueva_notificacion)
            session.commit()
            return nueva_notificacion.to_dict(), 200
        except Exception as e:
            session.rollback()
            return {"message": "Error al crear la notificación", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_todas(self) -> dict:
        """
        Obtiene todas las notificaciones.
        """
        session = get_session()
        try:
            notificaciones = session.query(TbNotificacion).all()
            return [notif.to_dict() for notif in notificaciones], 200
        except Exception as e:
            return {"message": "Error al obtener las notificaciones", "error": str(e)}, 500
        finally:
            session.close()
    
    def actualizar_notificacion(self, id_notificacion: int, campos_actualizados: dict) -> dict:
        """
        Actualiza una notificación existente.
        """
        session = get_session()
        try:
            notificacion_obj = session.query(TbNotificacion).filter(
                TbNotificacion.id_notificacion == id_notificacion
            ).first()
            
            if not notificacion_obj:
                return {"message": "Notificación no encontrada"}, 404
            
            # Actualizar los campos del objeto
            for key, value in campos_actualizados.items():
                if hasattr(notificacion_obj, key):
                    setattr(notificacion_obj, key, value)
                else:
                    return {"message": f"Campo '{key}' no válido"}, 400
            
            session.commit()
            return notificacion_obj.to_dict(), 200
        except Exception as e:
            session.rollback()
            return {"message": "Error al actualizar la notificación", "error": str(e)}, 500
        finally:
            session.close()
    
    def eliminar_notificacion(self, id_notificacion: int) -> dict:
        """
        Elimina una notificación.
        """
        session = get_session()
        try:
            notificacion_obj = session.query(TbNotificacion).filter(
                TbNotificacion.id_notificacion == id_notificacion
            ).first()
            
            if not notificacion_obj:
                return {"message": "Notificación no encontrada"}, 404
            
            session.delete(notificacion_obj)
            session.commit()
            return {"message": "Notificación eliminada correctamente"}, 200
        except Exception as e:
            session.rollback()
            return {"message": "Error al eliminar la notificación", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_por_id(self, id_notificacion: int) -> dict:
        """
        Obtiene una notificación específica por ID.
        """
        session = get_session()
        try:
            notificacion_obj = session.query(TbNotificacion).filter(
                TbNotificacion.id_notificacion == id_notificacion
            ).first()
            
            if not notificacion_obj:
                return {"message": "Notificación no encontrada"}, 404
            
            return notificacion_obj.to_dict(), 200
        except Exception as e:
            return {"message": "Error al obtener la notificación", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_por_estatus(self, id_estatus: int) -> dict:
        """
        Obtiene todas las notificaciones por estatus.
        """
        session = get_session()
        try:
            notificaciones = session.query(TbNotificacion).filter(
                TbNotificacion.id_estatus == id_estatus
            ).all()
            
            return [notif.to_dict() for notif in notificaciones], 200
        except Exception as e:
            return {"message": "Error al obtener las notificaciones", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_por_fecha(self, fecha_inicio: datetime, fecha_fin: datetime = None) -> dict:
        """
        Obtiene notificaciones por rango de fechas.
        """
        session = get_session()
        try:
            query = session.query(TbNotificacion).filter(
                TbNotificacion.fecha_notificacion >= fecha_inicio
            )
            
            if fecha_fin:
                query = query.filter(TbNotificacion.fecha_notificacion <= fecha_fin)
            
            notificaciones = query.all()
            return [notif.to_dict() for notif in notificaciones], 200
        except Exception as e:
            return {"message": "Error al obtener las notificaciones", "error": str(e)}, 500
        finally:
            session.close() 