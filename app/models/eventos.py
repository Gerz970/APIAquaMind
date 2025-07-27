from sqlalchemy import Column, Integer, String, DateTime, func, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TbEvento(Base):
    """
    Clase para manejar los eventos de los nodos
    """
    # Nombre de la tabla
    __tablename__ = 'tb_eventos'

    # Columnas de la tabla
    id_evento = Column(Integer, primary_key=True, autoincrement=True)
    id_nodo = Column(Integer, nullable=False)
    fecha_evento = Column(DateTime, nullable=False)
    id_estatus = Column(Integer, nullable=False, default=1)
    consumo = Column(DECIMAL(10, 2), nullable=False)
    unidad_medida = Column(String(10), nullable=False)

    def __init__(self, id_nodo: int, fecha_evento: DateTime, id_estatus: int, consumo: DECIMAL, unidad_medida: str):
        self.id_nodo = id_nodo
        self.fecha_evento = fecha_evento
        self.id_estatus = id_estatus
        self.consumo = consumo
        self.unidad_medida = unidad_medida

    def __repr__(self) -> str:
        return f"<Evento(id_nodo={self.id_nodo}, fecha_evento={self.fecha_evento}, id_estatus={self.id_estatus}, consumo={self.consumo}, unidad_medida={self.unidad_medida})>"

    def to_dict(self):
        """
        Convierte el objeto evento a un diccionario.
        """
        evento_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            evento_dict[column.name] = value
        return evento_dict