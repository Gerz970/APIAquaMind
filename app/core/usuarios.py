# Se crea la clase para manejar los usuarios
from typing import Optional, List
from utils.connectiondb import get_session
from datetime import datetime
from models.seguridad import TbUsuario


class UsuarioCRUD:
    def __init__(self):
        pass

    def crear_usuario(self, usuario_data: dict) -> dict:
        """
        Crea un nuevo usuario si no existe uno con el mismo correo o username.
        Devuelve el nuevo usuario en una lista o None si ya existe.
        """
        session = get_session()
        try:
            if self.obtener_por_correo(usuario_data["correo_electronico"]):
                return {"message": "El correo electrónico ya está registrado", "key": "correo_electronico"}, 400
            if self.obtener_por_username(usuario_data["username"]):
                return {"message": "El username ya está registrado", "key": "username"}, 400
            
            usuario = TbUsuario(**usuario_data)
            session.add(usuario)
            session.commit()
            session.refresh(usuario)

            return usuario.to_dict(exclude_fields=['password']), 200
        finally:
            session.close()


    def obtener_por_id(self, id_usuario: int) -> dict:
        """
        Retorna una lista con el usuario por ID si está activo.
        """
        session = get_session()
        try:
            usuario = session.query(TbUsuario).filter(
                TbUsuario.id_usuario == id_usuario,
                TbUsuario.id_estatus != 0
            ).first()
            return usuario.to_dict(exclude_fields=['password']) if usuario else None
        finally:
            session.close()

    def obtener_por_username(self, username: str) -> dict:
        """
        Retorna una lista con el usuario si está activo.
        """
        session = get_session()
        try:
            usuario = session.query(TbUsuario).filter(
                TbUsuario.username == username,
                TbUsuario.id_estatus != 0
            ).first()
            return usuario.to_dict(exclude_fields=['password']) if usuario else None
        finally:
            session.close()

    def obtener_por_correo(self, correo: str) -> dict:
        """
        Retorna una lista con el usuario por correo si está activo.
        """
        session = get_session()
        try:
            usuario = session.query(TbUsuario).filter(
                TbUsuario.correo_electronico == correo,
                TbUsuario.id_estatus != 0
            ).first()
            return usuario.to_dict(exclude_fields=['password']) if usuario else None
        finally:
            session.close()

    def obtener_todos(self) -> dict:
        """
        Retorna todos los usuarios activos como lista de objetos SQLAlchemy.
        """
        session = get_session()
        try:
            usuarios = session.query(TbUsuario).filter(TbUsuario.id_estatus != 0).all()
            return [usuario.to_dict(exclude_fields=['password']) for usuario in usuarios]
        finally:
            session.close()

    def actualizar_usuario(self, id_usuario: int, campos_actualizados: dict) -> dict:
        """
        Actualiza un usuario y devuelve la lista con el actualizado.
        """
        session = get_session()
        try:
            usuario = session.query(TbUsuario).filter(
                TbUsuario.id_usuario == id_usuario,
                TbUsuario.id_estatus != 0
            ).first()
            if not usuario:
                return None, 404

            for key, value in campos_actualizados.items():
                if key == "password":
                    usuario.password = value  # se encripta por setter
                elif hasattr(usuario, key):
                    setattr(usuario, key, value)

            session.commit()
            session.refresh(usuario)
            return usuario.to_dict(exclude_fields=['password']), 200
        finally:
            session.close()

    def eliminar_usuario(self, id_usuario: int) -> bool:
        """
        Realiza baja lógica del usuario (id_estatus = 0).
        """
        session = get_session()
        try:
            usuario = session.query(TbUsuario).filter(
                TbUsuario.id_usuario == id_usuario,
                TbUsuario.id_estatus != 0
            ).first()
            if not usuario:
                return False, 404

            usuario.id_estatus = 0
            session.commit()
            return True, 200
        finally:
            session.close()

    def reactivar_usuario(self, id_usuario: int) -> dict:
        """
        Reactiva un usuario previamente dado de baja (id_estatus = 1).
        """
        session = get_session()
        try:
            usuario = session.query(TbUsuario).filter(
                TbUsuario.id_usuario == id_usuario,
                TbUsuario.id_estatus == 0
            ).first()
            if not usuario:
                return None, 404

            usuario.id_estatus = 1
            session.commit()
            session.refresh(usuario)
            return usuario.to_dict(exclude_fields=['password']), 200
        finally:
            session.close()

    def verificar_credenciales(self, username: str, password: str) -> dict:
        """
        Verifica credenciales de login. Retorna lista con el usuario si es válido.
        """
        session = get_session()
        try:
            usuario = session.query(TbUsuario).filter(
                TbUsuario.username == username,
                TbUsuario.id_estatus != 0
            ).first()
            if usuario and usuario.verify_password(password):
                return usuario.to_dict(exclude_fields=['password']), 200
            return None, 401
        finally:
            session.close()
