"""
Rutas de sistema:
- GET /api/logs -> lee últimas 50 líneas de un log local (/app/logs/app.log)
- GET /api/endpoints -> lista rutas registradas
- POST /api/restart -> NO IMPLEMENTADO por seguridad (explico cómo hacerlo manual)
"""

from fastapi import APIRouter, FastAPI, Request
from fastapi import Depends
import os
from typing import List

router = APIRouter(prefix="/api")

LOG_PATH = "/app/logs/app.log"

@router.get("/logs")
def tail_logs(lines: int = 50):
    """
    Devuelve las últimas `lines` líneas del log si existe.
    (El contenedor escribe logs locales si configuras logging a archivo)
    """
    if not os.path.exists(LOG_PATH):
        return {"logs": [], "note": f"{LOG_PATH} no existe"}
    # lee archivo eficientemente desde el final
    with open(LOG_PATH, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        blocksize = 1024
        data = b""
        while size > 0 and lines > 0:
            step = min(blocksize, size)
            f.seek(size-step)
            chunk = f.read(step)
            data = chunk + data
            size -= step
            # count lines
            if data.count(b"\n") >= lines:
                break
        text = data.decode(errors="ignore")
    last = text.splitlines()[-lines:]
    return {"logs": last}

@router.get("/endpoints")
def list_endpoints(request: Request):
    """
    Lista los endpoints registrados (path + methods).
    """
    app: FastAPI = request.app
    routes = []
    for r in app.routes:
        # limit to user endpoints
        try:
            routes.append({"path": r.path, "name": getattr(r, "name", None)})
        except Exception:
            pass
    return {"endpoints": routes}

@router.post("/restart")
def restart_not_allowed():
    """
    No ejecuta 'docker restart' por seguridad. Si quieres habilitarlo, hay que montar el socket
    docker.sock en el contenedor y usar el SDK de docker con permisos. NO RECOMENDADO en entornos públicos.
    """
    return {"status": "disabled", "note": "Para reiniciar el contenedor desde la API debes montar /var/run/docker.sock y darle permisos. No está activado por seguridad."}
