from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from config import Config
import urllib
from contextlib import contextmanager


# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_engine():
    try:
        # Validar si los parámetros de conexión están configurados
        required_fields = ['SERVER', 'DATABASE', 'USER', 'PASSWORD']
        for field in required_fields:
            if not getattr(Config, field):
                raise ValueError(f"La configuración '{field}' no está establecida.")

        # Construir la cadena de conexión
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={Config.SERVER};"
            f"DATABASE={Config.DATABASE};"
            f"UID={Config.USER};"
            f"PWD={Config.PASSWORD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"  # Ignorar validación del certificado del servidor
            f"Connection Timeout=30;"
        )
        encoded_connection_string = urllib.parse.quote_plus(connection_string)

        # Crear el motor SQLAlchemy con configuración optimizada
        engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={encoded_connection_string}",
            pool_size=10,               # Número máximo de conexiones en el pool
            max_overflow=20,            # Conexiones adicionales permitidas
            pool_pre_ping=True,         # Verificar conexión antes de usar
            pool_recycle=3600,          # Reciclar conexiones cada hora
            echo=Config.DEBUG           # Mostrar SQL en modo debug
        )

        return engine

    except ValueError as ve:
        logger.error(f"Error en los parámetros de conexión: {ve}")
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
    
    return None


def get_session():
    """
    Obtiene una nueva sesión de base de datos.
    ⚠️ IMPORTANTE: Esta sesión debe ser cerrada manualmente después de usarla.
    """
    Session = sessionmaker(bind=get_engine())
    return Session()


@contextmanager
def get_db_session():
    """
    Context manager para manejar sesiones de base de datos de forma segura.
    
    Este context manager asegura que las sesiones se cierren automáticamente
    después de su uso, incluso si ocurre una excepción.
    
    Usage:
        with get_db_session() as session:
            # Usar la sesión para operaciones de BD
            users = session.query(User).all()
            # La sesión se cierra automáticamente al salir del bloque
    """
    session = get_session()
    try:
        yield session
    except Exception as e:
        logger.error(f"Error en operación de base de datos: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("Sesión de base de datos cerrada correctamente")

