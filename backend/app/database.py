"""
Archivo: database.py
Ubicación: backend/app/database.py

Descripción:
-------------
Este módulo gestiona la conexión con la base de datos MySQL.
Utiliza SQLAlchemy para crear el motor de conexión (engine),
la sesión local (SessionLocal) y la clase base para los modelos (Base).

Incluye además una función generadora get_db() que provee sesiones
de base de datos seguras para las rutas del backend, garantizando
el cierre correcto de la conexión al finalizar.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Cargar variables de entorno desde el archivo .env (usado fuera de Docker)
load_dotenv()

# ------------------------------------------------------------
# 1. Parámetros de conexión
# ------------------------------------------------------------
# Se definen las variables de entorno necesarias para conectar con la base de datos.
# Si alguna no existe en el entorno, se usan los valores por defecto definidos aquí.
DB_USER = os.getenv("DB_USER", "daniel")
DB_PASSWORD = os.getenv("DB_PASSWORD", "daniel123")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "lara_bs")

# ------------------------------------------------------------
# 2. Construcción de la URL de conexión compatible con SQLAlchemy
# ------------------------------------------------------------
# Formato general: dialect+driver://user:password@host:port/database
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ------------------------------------------------------------
# 3. Creación del motor (Engine)
# ------------------------------------------------------------
# El parámetro `echo=True` permite ver las consultas SQL en consola (solo en desarrollo).
# `future=True` habilita características más modernas de SQLAlchemy.
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
except SQLAlchemyError as e:
    # Si ocurre un error al crear el motor, se muestra en consola.
    print(f"Error al crear el motor de base de datos: {e}")
    engine = None

# ------------------------------------------------------------
# 4. Configuración del SessionLocal
# ------------------------------------------------------------
# Esta clase nos permitirá crear sesiones individuales de conexión con la base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------------------------------------
# 5. Clase Base
# ------------------------------------------------------------
# Usada como base para todos los modelos de la base de datos (ORM).
Base = declarative_base()

# ------------------------------------------------------------
# 6. Función get_db()
# ------------------------------------------------------------
# Esta función se usa como dependencia en FastAPI para inyectar una sesión de base de datos
# en cada petición. Garantiza el cierre seguro de la sesión incluso si ocurre una excepción.
def get_db():
    """
    Generador de sesión de base de datos.

    Retorna:
        Session: Una instancia activa de conexión a la base de datos.
    """
    db = None
    try:
        db = SessionLocal()
        yield db  # Se entrega la sesión al endpoint que la necesite
    except SQLAlchemyError as e:
        # Manejo de error en caso de que la sesión falle al inicializarse
        print(f"Error en la sesión de base de datos: {e}")
        raise e
    finally:
        # Cierre seguro de la conexión al finalizar el uso de la sesión
        if db is not None:
            db.close()
            db = None
