"""
Módulo de gestión de base de datos para APIAquaMind.

Este módulo implementa un gestor centralizado de base de datos que:
- Maneja conexiones de forma eficiente con pool de conexiones
- Proporciona sesiones de base de datos de forma segura
- Optimiza el rendimiento con configuración de pool
- Maneja errores de conexión de forma robusta

Características principales:
- Pool de conexiones para mejor rendimiento
- Configuración automática de timeouts
- Manejo seguro de sesiones
- Logging detallado de errores
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import logging
from config import Config
import urllib

# Configurar logger específico para base de datos
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestor centralizado de la base de datos.
    
    Esta clase maneja toda la configuración y gestión de conexiones
    a la base de datos SQL Server. Implementa un patrón Singleton
    para asegurar una única instancia del gestor.
    
    Características:
    - Pool de conexiones configurado
    - Manejo automático de reconexiones
    - Configuración optimizada para producción
    - Logging detallado de operaciones
    """
    
    def __init__(self):
        """
        Inicializar el gestor de base de datos.
        
        Crea el motor de SQLAlchemy y configura el pool de conexiones
        con parámetros optimizados para el rendimiento.
        """
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """
        Inicializar el motor de base de datos con configuración optimizada.
        
        Este método:
        1. Valida que todas las configuraciones requeridas estén presentes
        2. Construye la cadena de conexión para SQL Server
        3. Crea el motor SQLAlchemy con pool de conexiones
        4. Configura el session factory
        
        Raises:
            ValueError: Si faltan configuraciones requeridas
            Exception: Si hay error al conectar a la base de datos
        """
        try:
            # Validar que todos los parámetros de conexión estén configurados
            required_fields = ['SERVER', 'DATABASE', 'USER', 'PASSWORD']
            for field in required_fields:
                if not getattr(Config, field):
                    raise ValueError(f"La configuración '{field}' no está establecida.")
            
            # Construir la cadena de conexión para SQL Server
            # Esta cadena incluye todos los parámetros necesarios para conectar
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"  # Driver ODBC para SQL Server
                f"SERVER={Config.SERVER};"                     # Servidor de base de datos
                f"DATABASE={Config.DATABASE};"                 # Nombre de la base de datos
                f"UID={Config.USER};"                         # Usuario de la base de datos
                f"PWD={Config.PASSWORD};"                     # Contraseña del usuario
                f"Encrypt=yes;"                               # Habilitar encriptación
                f"TrustServerCertificate=yes;"                # Confiar en certificado del servidor
                f"Connection Timeout=30;"                     # Timeout de conexión en segundos
            )
            
            # Codificar la cadena de conexión para usarla en la URL
            encoded_connection_string = urllib.parse.quote_plus(connection_string)
            
            # Crear el motor SQLAlchemy con configuración optimizada
            self.engine = create_engine(
                f"mssql+pyodbc:///?odbc_connect={encoded_connection_string}",
                poolclass=QueuePool,        # Usar pool de conexiones en cola
                pool_size=10,               # Número máximo de conexiones en el pool
                max_overflow=20,            # Conexiones adicionales permitidas
                pool_pre_ping=True,         # Verificar conexión antes de usar
                pool_recycle=3600,          # Reciclar conexiones cada hora
                echo=Config.DEBUG           # Mostrar SQL en modo debug
            )
            
            # Crear session factory para generar sesiones de base de datos
            self.SessionLocal = sessionmaker(
                bind=self.engine,           # Vincular al motor creado
                autocommit=False,           # No hacer commit automático
                autoflush=False             # No hacer flush automático
            )
            
            logger.info("Motor de base de datos inicializado correctamente")
            
        except ValueError as ve:
            # Error de configuración - log y re-raise
            logger.error(f"Error en los parámetros de conexión: {ve}")
            raise
        except Exception as e:
            # Error de conexión - log y re-raise
            logger.error(f"Error al inicializar el motor de base de datos: {e}")
            raise
    
    def get_session(self):
        """
        Obtener una nueva sesión de base de datos.
        
        Esta sesión debe ser cerrada después de usarla para liberar
        la conexión del pool.
        
        Returns:
            Session: Sesión de SQLAlchemy lista para usar
            
        Raises:
            RuntimeError: Si la base de datos no ha sido inicializada
        """
        if not self.SessionLocal:
            raise RuntimeError("La base de datos no ha sido inicializada")
        return self.SessionLocal()
    
    def close_session(self, session):
        """
        Cerrar una sesión de base de datos de forma segura.
        
        Este método maneja la limpieza de la sesión y la liberación
        de la conexión al pool de conexiones.
        
        Args:
            session: Sesión de SQLAlchemy a cerrar
        """
        try:
            session.close()
        except Exception as e:
            logger.error(f"Error al cerrar la sesión: {e}")

# Instancia global del gestor de base de datos (patrón Singleton)
# Esta instancia se crea una sola vez y se reutiliza en toda la aplicación
db_manager = DatabaseManager()

def get_db_session():
    """
    Función helper para obtener una sesión de base de datos.
    
    Esta es la función principal que deben usar los servicios
    y modelos para obtener una sesión de base de datos.
    
    Returns:
        Session: Sesión de SQLAlchemy lista para usar
        
    Example:
        session = get_db_session()
        try:
            # Usar la sesión para operaciones de BD
            users = session.query(User).all()
        finally:
            close_db_session(session)
    """
    return db_manager.get_session()

def close_db_session(session):
    """
    Función helper para cerrar una sesión de base de datos.
    
    Siempre debe llamarse después de usar una sesión para
    liberar la conexión al pool.
    
    Args:
        session: Sesión de SQLAlchemy a cerrar
        
    Example:
        session = get_db_session()
        try:
            # Operaciones con la BD
            pass
        finally:
            close_db_session(session)  # Importante: siempre cerrar
    """
    db_manager.close_session(session) 