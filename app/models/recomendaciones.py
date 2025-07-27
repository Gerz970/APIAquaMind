from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TbRecomendacion(Base):
    __tablename__ = 'tb_recomendaciones'

    id_recomendacion = Column(Integer, primary_key=True, autoincrement=True)
    recomendacion = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=False)
    url_imagen = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=False)
    id_estatus = Column(Integer, nullable=False, default=1)

    def __init__(self, recomendacion: str, descripcion: str, url_imagen: str, icon: str, id_estatus: int = 1):
        self.recomendacion = recomendacion
        self.descripcion = descripcion
        self.url_imagen = url_imagen
        self.icon = icon
        self.id_estatus = id_estatus

    def __repr__(self) -> str:
        return f"<Recomendacion(id_recomendacion={self.id_recomendacion}, recomendacion={self.recomendacion[:30]}...)>"

    def to_dict(self, exclude_fields=None):
        """
        Convierte el objeto recomendación a un diccionario.
        
        Args:
            exclude_fields (list): Lista de campos a excluir de la serialización.
            
        Returns:
            dict: Diccionario con los datos de la recomendación.
        """
        if exclude_fields is None:
            exclude_fields = ['_sa_instance_state']
        
        recomendacion_dict = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # Convertir datetime a string si es necesario
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                recomendacion_dict[column.name] = value
        
        return recomendacion_dict

