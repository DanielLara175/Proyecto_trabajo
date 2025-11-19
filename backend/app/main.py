# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importación de routers existentes
from app.routers import usuarios, excel_router

# ------------------------------------------------------------
# Cola global de progreso usada por el router del Excel
# ------------------------------------------------------------
# Esta cola permite que el router excel_router envíe porcentaje de avance
# y que el frontend lo reciba mediante Server-Sent Events (SSE).
progress_queue = []   # Se usa como estructura FIFO simple

# Se expone esta cola al router excel_router para que pueda emitir progreso
excel_router.progress_queue = progress_queue
# ------------------------------------------------------------


# ------------------------------------------------------------
# Crear instancia única de FastAPI
# ------------------------------------------------------------
app = FastAPI(
    title="API Usuarios",
    description="API para gestión de usuarios y carga avanzada de Excel",
    version="1.0.0"
)

# ------------------------------------------------------------
# CORS - permitir comunicación con Angular
# ------------------------------------------------------------
origins = [
    "http://localhost:4200",     # Cliente Angular en modo desarrollo
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],     # Permite todos los métodos HTTP
    allow_headers=["*"],     # Permite todas las cabeceras personalizadas
)

# ------------------------------------------------------------
# Health check — útil para Docker
# ------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ------------------------------------------------------------
# Registrar routers
# ------------------------------------------------------------
# Router de usuarios
app.include_router(usuarios.router)

# Router del cargador avanzado de Excel
app.include_router(excel_router.router)