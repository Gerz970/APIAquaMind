from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import bcrypt

Base = declarative_base()

class TbUsuario(Base):
    __tablename__ = 'tb_usuario'

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(25), nullable=False, unique=True)
    _password = Column("password", Text, nullable=False)
    correo_electronico = Column(String(50), nullable=False, unique=True)
    nombre = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=True, default='')
    fecha_nacimiento = Column(DateTime, nullable=True)
    id_tipo_usuario = Column(Integer, nullable=False, default=1)
    id_estatus = Column(Integer, nullable=False, default=1)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())


    def __init__(
        self,
        username: str,
        password: str,
        correo_electronico: str,
        nombre: str = '',
        apellido_paterno: str = '',
        apellido_materno: str = '',
        fecha_nacimiento: DateTime = None,
        id_tipo_usuario: int = 1,
        id_estatus: int = 1,
        fecha_registro: DateTime = None
    ):
        # Asignaciones con valores por defecto
        self.username = username
        self.password = password  # se encripta en el setter
        self.correo_electronico = correo_electronico
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.fecha_nacimiento = fecha_nacimiento
        self.id_tipo_usuario = id_tipo_usuario
        self.id_estatus = id_estatus
        if fecha_registro:
            self.fecha_registro = fecha_registro

    @property
    def password(self) -> str:
        """
        Getter de contraseña (hasheada).
        """
        return self._password

    @password.setter
    def password(self, raw_password: str):
        self._password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode('utf-8'), self._password.encode('utf-8'))

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id_usuario}, username={self.username})>"

    def to_dict(self, exclude_fields=None):
        """
        Convierte el objeto usuario a un diccionario.
        
        Args:
            exclude_fields (list): Lista de campos a excluir de la serialización.
            
        Returns:
            dict: Diccionario con los datos del usuario.
        """
        if exclude_fields is None:
            exclude_fields = ['_password', '_sa_instance_state']
        
        user_dict = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # Convertir datetime a string si es necesario
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                user_dict[column.name] = value
        
        return user_dict