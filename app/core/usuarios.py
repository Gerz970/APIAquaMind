# Se crea la clase para manejar los usuarios
from typing import Optional, List
from utils.connectiondb import get_session
from datetime import datetime
from models.seguridad import TbUsuario


class UsuarioCRUD:
    def __init__(self):
        self.db = get_session()

    def crear_usuario(self, usuario_data: dict) -> Optional[List[TbUsuario]]:
        """
        Crea un nuevo usuario si no existe uno con el mismo correo o username.
        Devuelve el nuevo usuario en una lista o None si ya existe.
        """
        if self.obtener_por_correo(usuario_data["correo_electronico"]):
            return {"message": "El correo electrónico ya está registrado", "key": "correo_electronico", "status": 400}
        if self.obtener_por_username(usuario_data["username"]):
            return {"message": "El username ya está registrado", "key": "username", "status": 400}
        
        usuario = TbUsuario(**usuario_data)
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)

        return [usuario.to_dict(exclude_fields=['password'])]

    def obtener_por_id(self, id_usuario: int) -> Optional[List[TbUsuario]]:
        """
        Retorna una lista con el usuario por ID si está activo.
        """
        usuario = self.db.query(TbUsuario).filter(
            TbUsuario.id_usuario == id_usuario,
            TbUsuario.id_estatus != 0
        ).first()
        return [usuario] if usuario else None

    def obtener_por_username(self, username: str) -> Optional[List[TbUsuario]]:
        """
        Retorna una lista con el usuario si está activo.
        """
        usuario = self.db.query(TbUsuario).filter(
            TbUsuario.username == username,
            TbUsuario.id_estatus != 0
        ).first()
        return [usuario] if usuario else None

    def obtener_por_correo(self, correo: str) -> Optional[List[TbUsuario]]:
        """
        Retorna una lista con el usuario por correo si está activo.
        """
        usuario = self.db.query(TbUsuario).filter(
            TbUsuario.correo_electronico == correo,
            TbUsuario.id_estatus != 0
        ).first()
        return [usuario] if usuario else None

    def obtener_todos(self) -> List[TbUsuario]:
        """
        Retorna todos los usuarios activos como lista, a excepción de la contraseña
        """
        usuarios = self.db.query(TbUsuario).filter(TbUsuario.id_estatus != 0).all()
        return [usuario.to_dict(exclude_fields=['password']) for usuario in usuarios]   

    def actualizar_usuario(self, id_usuario: int, campos_actualizados: dict) -> Optional[List[TbUsuario]]:
        """
        Actualiza un usuario y devuelve la lista con el actualizado.
        """
        usuario = self.db.query(TbUsuario).filter(
            TbUsuario.id_usuario == id_usuario,
            TbUsuario.id_estatus != 0
        ).first()
        if not usuario:
            return None

        for key, value in campos_actualizados.items():
            if key == "password":
                usuario.password = value  # se encripta por setter
            elif hasattr(usuario, key):
                setattr(usuario, key, value)

        self.db.commit()
        self.db.refresh(usuario)
        return [usuario]

    def eliminar_usuario(self, id_usuario: int) -> bool:
        """
        Realiza baja lógica del usuario (id_estatus = 0).
        """
        usuario = self.db.query(TbUsuario).filter(
            TbUsuario.id_usuario == id_usuario,
            TbUsuario.id_estatus != 0
        ).first()
        if not usuario:
            return False

        usuario.id_estatus = 0
        self.db.commit()
        return True

    def reactivar_usuario(self, id_usuario: int) -> Optional[List[TbUsuario]]:
        """
        Reactiva un usuario previamente dado de baja (id_estatus = 1).
        """
        usuario = self.db.query(TbUsuario).filter(
            TbUsuario.id_usuario == id_usuario,
            TbUsuario.id_estatus == 0
        ).first()
        if not usuario:
            return None

        usuario.id_estatus = 1
        self.db.commit()
        self.db.refresh(usuario)
        return [usuario]

    def verificar_credenciales(self, username: str, password: str) -> Optional[List[TbUsuario]]:
        """
        Verifica credenciales de login. Retorna lista con el usuario si es válido.
        """
        usuario = self.db.query(TbUsuario).filter(
            TbUsuario.username == username,
            TbUsuario.id_estatus != 0
        ).first()
        if usuario and usuario.verify_password(password):
            return [usuario]
        return None
