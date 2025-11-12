"""
Archivo: config.py
Ubicación: backend/app/config.py

Descripción:
-------------
Este módulo centraliza la configuración del proyecto backend.
Usa Pydantic para cargar variables desde el entorno o el archivo .env.
Esto permite mantener las credenciales y parámetros de conexión desacoplados del código fuente.
"""

from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Clase que define las variables de entorno requeridas por la aplicación.
    Pydantic valida y convierte automáticamente los tipos de datos.
    """
    
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Otras variables opcionales para ampliar en el futuro
    APP_NAME: str = "FastAPI Backend"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    class Config:
        """
        Configuración interna de Pydantic.
        Permite cargar variables desde el archivo .env o directamente del entorno del contenedor.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Devuelve una instancia única (cacheada) de Settings.
    Se usa lru_cache para evitar recargar el archivo .env múltiples veces durante la ejecución.
    """
    return Settings()


# Prueba manual opcional (solo para desarrollo local)
# Ejecutar: python backend/app/config.py
if __name__ == "__main__":
    settings = get_settings()
    print("Configuración cargada correctamente:")
    print(f"Base de datos: {settings.DB_USER}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
