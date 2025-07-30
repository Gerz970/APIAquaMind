from sqlalchemy import Column, Integer, String, DateTime, func, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class TbNotificacion(Base):
    """
    Clase para manejar las notificaciones
    """
    # Nombre de la tabla
    __tablename__ = 'tb_notificaciones'

    # Columnas de la tabla
    id_notificacion = Column(Integer, primary_key=True, autoincrement=True)
    notificacion = Column(String(255), nullable=False)
    mensaje = Column(String(255), nullable=False)
    fecha_notificacion = Column(DateTime, nullable=False)
    id_estatus = Column(Integer, nullable=False, default=1)


    def __init__(self, notificacion: str, mensaje: str, fecha_notificacion: DateTime = None, id_estatus: int = 1):
        self.notificacion = notificacion
        self.mensaje = mensaje
        self.fecha_notificacion = fecha_notificacion if fecha_notificacion else datetime.now()
        self.id_estatus = id_estatus

    def __repr__(self) -> str:
        return f"<Notificacion(notificacion={self.notificacion}, mensaje={self.mensaje}, fecha_notificacion={self.fecha_notificacion}, id_estatus={self.id_estatus})>"

    def to_dict(self):
        """
        Convierte el objeto notificacion a un diccionario.
        """
        notificacion_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            notificacion_dict[column.name] = value
        return notificacion_dict