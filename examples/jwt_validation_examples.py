"""
Ejemplos de uso de los endpoints de validación JWT.

Este archivo contiene ejemplos de cómo usar los endpoints de validación
de tokens JWT que acabamos de crear.
"""

import requests
import json

# Configuración base
BASE_URL = "http://localhost:5000/api/v1"
HEADERS = {
    "Content-Type": "application/json"
}

def example_login():
    """
    Ejemplo de login para obtener un token JWT.
    """
    print("=== Ejemplo de Login ===")
    
    login_data = {
        "user": "usuario123",
        "password": "MiContraseña123"
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers=HEADERS
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["token"]
        print(f"Login exitoso. Token: {token[:50]}...")
        return token
    else:
        print(f"Error en login: {response.status_code} - {response.text}")
        return None

def example_validate_token(token):
    """
    Ejemplo de validación de token usando el endpoint /auth/validate.
    """
    print("\n=== Ejemplo de Validación de Token ===")
    
    validate_data = {
        "token": token
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/validate",
        json=validate_data,
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def example_verify_token(token):
    """
    Ejemplo de verificación de token usando el endpoint /auth/verify.
    """
    print("\n=== Ejemplo de Verificación de Token ===")
    
    # Agregar el token al header Authorization
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(
        f"{BASE_URL}/auth/verify",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def example_invalid_token():
    """
    Ejemplo de validación con token inválido.
    """
    print("\n=== Ejemplo de Token Inválido ===")
    
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.token"
    
    validate_data = {
        "token": invalid_token
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/validate",
        json=validate_data,
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def example_expired_token():
    """
    Ejemplo de validación con token expirado.
    """
    print("\n=== Ejemplo de Token Expirado ===")
    
    # Este es un token de ejemplo que probablemente esté expirado
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiaWF0IjoxNjE2MTYxNjE2LCJleHAiOjE2MTYxNjE2MTZ9.expired"
    
    validate_data = {
        "token": expired_token
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/validate",
        json=validate_data,
        headers=HEADERS
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def example_get_current_user(token):
    """
    Ejemplo de obtención de información del usuario actual.
    """
    print("\n=== Ejemplo de Usuario Actual ===")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """
    Función principal que ejecuta todos los ejemplos.
    """
    print("Ejemplos de Validación JWT para APIAquaMind")
    print("=" * 50)
    
    # 1. Hacer login para obtener un token
    token = example_login()
    
    if token:
        # 2. Validar el token usando el endpoint /auth/validate
        example_validate_token(token)
        
        # 3. Verificar el token usando el endpoint /auth/verify
        example_verify_token(token)
        
        # 4. Obtener información del usuario actual
        example_get_current_user(token)
    
    # 5. Ejemplos con tokens inválidos
    example_invalid_token()
    example_expired_token()

if __name__ == "__main__":
    main() 