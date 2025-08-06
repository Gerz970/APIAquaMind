from sqlalchemy import Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TbConfiguracion(Base):
    __tablename__ = 'tb_configuraciones'

    id_configuracion = Column(Integer, primary_key=True, autoincrement=True)
    configuracion = Column(String(200), nullable=False, unique=True)
    valor = Column(String(200), nullable=True)
    id_estatus = Column(Integer, nullable=False, default=1)
    descripcion = Column(String(200), nullable=True)

    def __init__(self, configuracion: str, valor: str = None, id_estatus: int = 1, descripcion: str = None):
        self.configuracion = configuracion
        self.valor = valor
        self.id_estatus = id_estatus
        self.descripcion = descripcion

    def __repr__(self) -> str:
        return f"<Configuracion(id_configuracion={self.id_configuracion}, configuracion={self.configuracion})>"

    def to_dict(self, exclude_fields=None):
        """
        Convierte el objeto configuración a un diccionario.
        
        Args:
            exclude_fields (list): Lista de campos a excluir de la serialización.
            
        Returns:
            dict: Diccionario con los datos de la configuración.
        """
        if exclude_fields is None:
            exclude_fields = ['_sa_instance_state']
        
        config_dict = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # Convertir datetime a string si es necesario
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                config_dict[column.name] = value
        
        return config_dict 