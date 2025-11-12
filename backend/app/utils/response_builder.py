# backend/app/utils/response_builder.py

# Importar tipos para anotaciones estáticas y documentación.
from typing import Any, Optional, Dict

def build_response(
    status: int,
    type: str,
    title: str,
    message: str,
    data: Optional[Any] = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Construye y retorna una respuesta estandarizada para la API.

    Parámetros:
        status (int): Código HTTP de la respuesta (ej. 200, 404, 500).
        type (str): Tipo lógico de la respuesta: "success", "error", "info", "warning".
        title (str): Título breve y descriptivo de la respuesta para el cliente.
        message (str): Mensaje principal que resume la respuesta.
        data (Optional[Any]): Datos adicionales que la API devuelve (puede ser dict, list, None).
        error (Optional[str]): Mensaje técnico o detalle del error (opcional).

    Retorna:
        Dict[str, Any]: Diccionario con la estructura uniforme que la API devolverá en JSON.
    """

    # Aseguramos que el status sea un entero; lo forzamos explícitamente.
    status_int = int(status)

    # Convertimos el tipo a str para evitar problemas si se pasa otro tipo.
    type_str = str(type)

    # Convertimos título y mensaje a string para garantizar consistencia.
    title_str = str(title)
    message_str = str(message)

    # Estructura estándar acordada para todas las respuestas de la API.
    response: Dict[str, Any] = {
        "status": status_int,        # Código HTTP numérico
        "type": type_str,            # Tipo lógico: success/error/info/warning
        "title": title_str,          # Título breve
        "message": message_str,      # Mensaje principal
        "data": data,                # Datos adicionales o None
        "error": error               # Detalle técnico del error o None
    }

    # Retornamos el diccionario listo para serializar a JSON en FastAPI.
    return response
