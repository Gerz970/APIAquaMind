from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from config import Config
import urllib


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

        # Crear el motor SQLAlchemy
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={encoded_connection_string}")

        return engine

    except ValueError as ve:
        logger.error(f"Error en los parámetros de conexión: {ve}")
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
    
    return None


def get_session():
    Session = sessionmaker(bind=get_engine())
    return Session()

