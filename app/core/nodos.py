# Se crea la clase para manejar los usuarios
from typing import Optional, List
from utils.connectiondb import get_session
from datetime import datetime
from models.nodos import TbNodo


class NodoCRUD:
    def __init__(self):
        pass

    def crear_nodo(self, nodo_data: dict) -> dict:
        """
        Crea un nuevo nodo si no existe uno con el mismo nombre.
        Devuelve el nuevo nodo en una lista o None si ya existe.
        """
        session = get_session()
        try:
            nuevo_nodo = TbNodo(**nodo_data)
            session.add(nuevo_nodo)
            session.commit()
            return nuevo_nodo.to_dict(), 200
        finally:
            session.close()
    
    def obtener_todos(self) -> dict:
        session = get_session()
        try:
            return [nodo.to_dict() for nodo in session.query(TbNodo).all()], 200
        finally:
            session.close()
    
    def actualizar_nodo(self, id_nodo: int, campos_actualizados: dict) -> dict:
        session = get_session()
        try:
            # Obtener el objeto TbNodo directamente de la base de datos
            nodo_obj = session.query(TbNodo).filter(TbNodo.id_nodo == id_nodo).first()
            if not nodo_obj:
                return None, 404
            
            # Actualizar los campos del objeto
            for key, value in campos_actualizados.items():
                if hasattr(nodo_obj, key):
                    setattr(nodo_obj, key, value)
                else:
                    return None, 400
            
            session.commit()
            return nodo_obj.to_dict(), 200
        finally:
            session.close()
    
    def eliminar_nodo(self, id_nodo: int) -> dict:
        session = get_session()
        try:
            nodo_obj = session.query(TbNodo).filter(TbNodo.id_nodo == id_nodo).first()
            if not nodo_obj:
                return {"message": "Nodo no encontrado"}, 404
            session.delete(nodo_obj)
            session.commit()
            return {"message": "Nodo eliminado correctamente"}, 200
        finally:
            session.close()
    
    def obtener_por_id(self, id_nodo: int) -> dict:
        session = get_session()
        try:
            nodo_obj = session.query(TbNodo).filter(TbNodo.id_nodo == id_nodo).first()
            if not nodo_obj:
                return {"message": "Nodo no encontrado"}, 404
            return nodo_obj.to_dict(), 200
        except Exception as e:
            return {"message": "Error al obtener el nodo", "error": str(e)}, 500
        finally:
            session.close()
    
    def obtener_nodo_por_descripcion(self, descripcion: str) -> dict:
        session = get_session()
        try:
            nodo_obj = session.query(TbNodo).filter(TbNodo.descripcion == descripcion).first()
            if not nodo_obj:
                return {"message": "Nodo no encontrado"}, 404
            return nodo_obj.to_dict(), 200
        except Exception as e:
            return {"message": "Error al obtener el nodo", "error": str(e)}, 500
        finally:
            session.close()