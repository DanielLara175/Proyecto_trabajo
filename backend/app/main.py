# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios

app = FastAPI(title="API Usuarios")

@app.get("/health")
def health_check():
    return {"status": "ok"}

#  CORS - solo una vez
origins = [
    "http://localhost:4200",     #  Angular
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

#  Registrar el router de los usuarios
app.include_router(usuarios.router)
