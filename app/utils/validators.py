"""
Módulo de validaciones para APIAquaMind.

Este módulo contiene todas las validaciones de datos de entrada:
- Validación de emails
- Validación de contraseñas (fortaleza)
- Validación de usernames
- Validación de datos de usuario completos
- Validación de datos de login

Las validaciones son importantes para:
- Seguridad: Prevenir datos maliciosos
- Integridad: Asegurar datos válidos en la BD
- UX: Proporcionar mensajes de error claros
- Mantenimiento: Centralizar reglas de validación
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class ValidationError(Exception):
    """
    Excepción personalizada para errores de validación.
    
    Esta excepción se usa para indicar que los datos proporcionados
    no cumplen con las reglas de validación establecidas.
    
    Attributes:
        message: Mensaje descriptivo del error
        field: Campo específico que causó el error (opcional)
    """
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class UserValidator:
    """
    Validador para datos de usuario.
    
    Esta clase contiene métodos estáticos para validar diferentes
    aspectos de los datos de usuario antes de guardarlos en la BD.
    
    Características:
    - Validaciones de formato (email, username)
    - Validaciones de fortaleza (contraseña)
    - Validaciones de longitud y caracteres permitidos
    - Mensajes de error en español
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validar formato de email usando expresiones regulares.
        
        Esta validación verifica que el email tenga un formato válido:
        - Debe contener un @
        - Debe tener un dominio válido
        - Debe tener una extensión de dominio válida
        
        Args:
            email: String con el email a validar
            
        Returns:
            bool: True si el email es válido, False en caso contrario
            
        Example:
            is_valid = UserValidator.validate_email("usuario@dominio.com")
        """
        # Patrón regex para validar emails
        # ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
        # ^ - Inicio de string
        # [a-zA-Z0-9._%+-]+ - Caracteres permitidos antes del @ (uno o más)
        # @ - Símbolo @ obligatorio
        # [a-zA-Z0-9.-]+ - Caracteres del dominio (uno o más)
        # \. - Punto antes de la extensión
        # [a-zA-Z]{2,} - Extensión de al menos 2 caracteres
        # $ - Fin de string
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validar fortaleza de contraseña.
        
        Esta validación verifica que la contraseña cumpla con los requisitos
        de seguridad establecidos para proteger las cuentas de usuario.
        
        Requisitos de fortaleza:
        - Mínimo 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        
        Args:
            password: String con la contraseña a validar
            
        Returns:
            Tuple[bool, str]: (es_válida, mensaje_error)
            - es_válida: True si cumple todos los requisitos
            - mensaje_error: Descripción del error si no es válida
            
        Example:
            is_valid, error_msg = UserValidator.validate_password("MiPass123")
            if not is_valid:
                # Manejar el error según sea necesario
                pass
        """
        # Verificar longitud mínima
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        # Verificar que contenga al menos una mayúscula
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe contener al menos una mayúscula"
        
        # Verificar que contenga al menos una minúscula
        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe contener al menos una minúscula"
        
        # Verificar que contenga al menos un número
        if not re.search(r'\d', password):
            return False, "La contraseña debe contener al menos un número"
        
        # Si pasa todas las validaciones, es válida
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validar formato de username.
        
        Esta validación asegura que el username cumpla con las reglas
        establecidas para ser válido en el sistema.
        
        Reglas del username:
        - Entre 3 y 25 caracteres
        - Solo letras, números y guiones bajos
        - No puede estar vacío
        
        Args:
            username: String con el username a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
            
        Example:
            is_valid, error_msg = UserValidator.validate_username("mi_usuario123")
        """
        # Verificar longitud mínima
        if len(username) < 3:
            return False, "El username debe tener al menos 3 caracteres"
        
        # Verificar longitud máxima
        if len(username) > 25:
            return False, "El username no puede exceder 25 caracteres"
        
        # Verificar caracteres permitidos (solo letras, números y _)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "El username solo puede contener letras, números y guiones bajos"
        
        return True, ""
    
    @staticmethod
    def validate_user_data(data: Dict) -> List[Dict[str, str]]:
        """
        Validar datos completos de usuario.
        
        Este método realiza todas las validaciones necesarias para
        un conjunto completo de datos de usuario antes de guardarlo
        en la base de datos.
        
        Validaciones realizadas:
        - Campos requeridos presentes
        - Formato de email válido
        - Username válido
        - Contraseña fuerte
        - Longitudes de campos respetadas
        
        Args:
            data: Diccionario con los datos del usuario
            
        Returns:
            List[Dict]: Lista de errores encontrados
            Cada error tiene: {"field": "campo", "message": "descripción"}
            
        Example:
            errors = UserValidator.validate_user_data({
                "username": "usuario",
                "password": "pass123",
                "email": "test@test.com"
            })
            if errors:
                for error in errors:
                    # Manejar el error según sea necesario
                    pass
        """
        errors = []
        
        # Validar campos requeridos
        # Estos campos son obligatorios para crear un usuario
        required_fields = ['username', 'password', 'correo_electronico', 'nombre', 'apellido_paterno']
        for field in required_fields:
            if not data.get(field):
                errors.append({
                    "field": field,
                    "message": f"El campo {field} es requerido"
                })
        
        # Validar formato de email si está presente
        if data.get('correo_electronico'):
            if not UserValidator.validate_email(data['correo_electronico']):
                errors.append({
                    "field": "correo_electronico",
                    "message": "El formato del email no es válido"
                })
        
        # Validar username si está presente
        if data.get('username'):
            is_valid, message = UserValidator.validate_username(data['username'])
            if not is_valid:
                errors.append({
                    "field": "username",
                    "message": message
                })
        
        # Validar contraseña si está presente
        if data.get('password'):
            is_valid, message = UserValidator.validate_password(data['password'])
            if not is_valid:
                errors.append({
                    "field": "password",
                    "message": message
                })
        
        # Validar longitudes de campos de texto
        # Estos límites están basados en la estructura de la BD
        field_lengths = {
            'nombre': 50,           # Máximo 50 caracteres
            'apellido_paterno': 50, # Máximo 50 caracteres
            'apellido_materno': 50  # Máximo 50 caracteres
        }
        
        for field, max_length in field_lengths.items():
            if data.get(field) and len(data[field]) > max_length:
                errors.append({
                    "field": field,
                    "message": f"El campo {field} no puede exceder {max_length} caracteres"
                })
        
        return errors

class LoginValidator:
    """
    Validador para datos de login.
    
    Esta clase contiene validaciones específicas para el proceso
    de autenticación (login) de usuarios.
    
    Las validaciones son más simples que las de usuario completo
    ya que solo necesitamos verificar que los campos requeridos
    estén presentes.
    """
    
    @staticmethod
    def validate_login_data(data: Dict) -> List[Dict[str, str]]:
        """
        Validar datos de login.
        
        Para el login solo necesitamos verificar que:
        - El campo 'user' esté presente
        - El campo 'password' esté presente
        
        Args:
            data: Diccionario con los datos de login
            
        Returns:
            List[Dict]: Lista de errores encontrados
            
        Example:
            errors = LoginValidator.validate_login_data({
                "user": "usuario",
                "password": "contraseña"
            })
        """
        errors = []
        
        # Verificar que el campo 'user' esté presente
        if not data.get('username'):
            errors.append({
                "field": "username",
                "message": "El campo username es requerido"
            })
        
        # Verificar que el campo 'password' esté presente
        if not data.get('password'):
            errors.append({
                "field": "password",
                "message": "El campo password es requerido"
            })
        
        return errors 