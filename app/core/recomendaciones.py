# Se crea la clase para manejar las recomendaciones
from typing import Optional, List
from utils.connectiondb import get_session
from datetime import datetime
from models.recomendaciones import TbRecomendacion
from sqlalchemy import func


class RecomendacionesCRUD:
    def __init__(self):
        # ❌ Eliminamos la sesión del constructor para evitar fugas de memoria
        pass

    def crear_recomendacion(self, recomendacion_data: dict) -> tuple:
        """
        Crea una nueva recomendación si no existe una con el mismo nombre.
        Devuelve la nueva recomendación o error si ya existe.
        """
        session = get_session()
        try:
            # Verificar si ya existe una recomendación con el mismo nombre
            if self.obtener_por_nombre(recomendacion_data["recomendacion"]):
                return {"message": "Ya existe una recomendación con ese nombre", "key": "recomendacion"}, 400
            
            nueva_recomendacion = TbRecomendacion(**recomendacion_data)
            session.add(nueva_recomendacion)
            session.commit()
            session.refresh(nueva_recomendacion)

            return nueva_recomendacion.to_dict(), 200
        finally:
            session.close()
    
    
    def actualizar_recomendacion(self, id_recomendacion: int, recomendacion_data: dict) -> tuple:
        """
        Actualiza una recomendación existente.
        """
        session = get_session()
        try:
            recomendacion = session.query(TbRecomendacion).filter(
                TbRecomendacion.id_recomendacion == id_recomendacion,
                TbRecomendacion.id_estatus != 0
            ).first()
            
            if not recomendacion:
                return None, 404

            for key, value in recomendacion_data.items():
                if hasattr(recomendacion, key):
                    setattr(recomendacion, key, value)
            
            session.commit()
            session.refresh(recomendacion)
            return recomendacion.to_dict(), 200
        finally:
            session.close()
    
    def eliminar_recomendacion(self, id_recomendacion: int) -> tuple:
        """
        Realiza baja lógica de la recomendación (id_estatus = 0).
        """
        session = get_session()
        try:
            recomendacion = session.query(TbRecomendacion).filter(
                TbRecomendacion.id_recomendacion == id_recomendacion,
                TbRecomendacion.id_estatus != 0
            ).first()
            
            if not recomendacion:
                return False, 404

            recomendacion.id_estatus = 0
            session.commit()
            return True, 200
        finally:
            session.close()
    
    def reactivar_recomendacion(self, id_recomendacion: int) -> tuple:
        """
        Reactiva una recomendación previamente dada de baja (id_estatus = 1).
        """
        session = get_session()
        try:
            recomendacion = session.query(TbRecomendacion).filter(
                TbRecomendacion.id_recomendacion == id_recomendacion,
                TbRecomendacion.id_estatus == 0
            ).first()
            
            if not recomendacion:
                return None, 404

            recomendacion.id_estatus = 1
            session.commit()
            session.refresh(recomendacion)
            return recomendacion.to_dict(), 200
        finally:
            session.close()
    
    def obtener_por_id(self, id_recomendacion: int) -> dict:
        """
        Retorna la recomendación por ID si está activa.
        """
        session = get_session()
        try:
            recomendacion = session.query(TbRecomendacion).filter(
                TbRecomendacion.id_recomendacion == id_recomendacion,
                TbRecomendacion.id_estatus != 0
            ).first()
            return recomendacion.to_dict() if recomendacion else None
        finally:
            session.close()

    def obtener_por_nombre(self, nombre: str) -> dict:
        """
        Retorna la recomendación por nombre si está activa.
        """
        session = get_session()
        try:
            recomendacion = session.query(TbRecomendacion).filter(
                TbRecomendacion.recomendacion == nombre,
                TbRecomendacion.id_estatus != 0
            ).first()
            return recomendacion.to_dict() if recomendacion else None
        finally:
            session.close()
    
    def obtener_todas(self) -> List[dict]:
        """
        Retorna todas las recomendaciones activas.
        """
        session = get_session()
        try:
            recomendaciones = session.query(TbRecomendacion).filter(TbRecomendacion.id_estatus != 0).all()
            return [recomendacion.to_dict() for recomendacion in recomendaciones]
        finally:
            session.close()
    
    def obtener_recomendaciones_aleatorias(self, cantidad: int) -> List[dict]:
        """
        Retorna una cantidad específica de recomendaciones aleatorias activas.
        """
        session = get_session()
        try:
            # Para SQL Server usamos func.newid() en lugar de func.random()
            recomendaciones = session.query(TbRecomendacion).filter(
                TbRecomendacion.id_estatus != 0
            ).order_by(func.newid()).limit(cantidad).all()
            return [recomendacion.to_dict() for recomendacion in recomendaciones]
        finally:
            session.close()