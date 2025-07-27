from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TbNodo(Base):
    __tablename__ = 'tb_nodos'

    id_nodo = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(String(255), nullable=True)
    id_estatus = Column(Integer, nullable=False, default=1)
    fecha_registro = Column(DateTime, nullable=False)

    def __init__(self, nombre: str, descripcion: str = '', id_estatus: int = 1, fecha_registro: DateTime = None):
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_estatus = id_estatus
        self.fecha_registro = fecha_registro

    def __repr__(self) -> str:
        return f"<Nodo(id_nodo={self.id_nodo}, nombre={self.nombre})>"

    def to_dict(self, exclude_fields=None):
        """
        Convierte el objeto nodo a un diccionario.
        
        Args:
            exclude_fields (list): Lista de campos a excluir de la serialización.
            
        Returns:
            dict: Diccionario con los datos del nodo.
        """
        if exclude_fields is None:
            exclude_fields = ['_sa_instance_state']
        
        nodo_dict = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # Convertir datetime a string si es necesario
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                nodo_dict[column.name] = value
        
        return nodo_dict

    