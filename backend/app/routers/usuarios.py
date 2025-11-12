from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# ✅ Importación correcta de schemas y crud
from app import crud, schemas
from app.database import get_db

# Crear router para las rutas relacionadas con usuarios
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# 🧩 Crear un nuevo usuario
@router.post("/", response_model=schemas.UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la base de datos.
    """
    return crud.crear_usuario(db, usuario)


# 📋 Listar todos los usuarios
@router.get("/", response_model=List[schemas.UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    """
    Retorna una lista de todos los usuarios registrados.
    """
    return crud.obtener_usuarios(db)
    # Si tu función se llama get_usuarios usa esta línea:
    # return crud.get_usuarios(db)


# ❌ Eliminar un usuario por ID
@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Elimina un usuario existente por su ID.
    """
    return crud.borrar_usuario(db, usuario_id)
