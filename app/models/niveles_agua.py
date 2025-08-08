from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TbNivelAgua(Base):
    __tablename__ = 'tb_niveles_agua'

    id_nivel = Column(Integer, primary_key=True, autoincrement=True)
    distancia = Column(Numeric(18, 2), nullable=True)
    desnivel = Column(String(25), nullable=True)
    bomba = Column(String(25), nullable=True)
    compuerta = Column(String(25), nullable=True)
    nivel_estado = Column(String(25), nullable=True)
    porcentaje_agua = Column(Numeric(18, 2), nullable=True)
    fecha = Column(DateTime, default=func.getdate())

    def __init__(self, distancia=None, desnivel=None, bomba=None, compuerta=None, 
                 nivel_estado=None, porcentaje_agua=None, fecha=None):
        self.distancia = distancia
        self.desnivel = desnivel
        self.bomba = bomba
        self.compuerta = compuerta
        self.nivel_estado = nivel_estado
        self.porcentaje_agua = porcentaje_agua
        self.fecha = fecha

    def __repr__(self):
        return f"<TbNivelAgua(id_nivel={self.id_nivel}, distancia={self.distancia}, nivel_estado='{self.nivel_estado}')>"

    def to_dict(self):
        """
        Convertir el objeto a diccionario.
        """
        return {
            'id_nivel': self.id_nivel,
            'distancia': float(self.distancia) if self.distancia is not None else 0.0,
            'desnivel': self.desnivel,
            'bomba': self.bomba,
            'compuerta': self.compuerta,
            'nivel_estado': self.nivel_estado,
            'porcentaje_agua': float(self.porcentaje_agua) if self.porcentaje_agua is not None else 0.0,
            'fecha': self.fecha.isoformat() if self.fecha else None
        } 