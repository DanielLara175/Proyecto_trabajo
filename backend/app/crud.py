# app/crud.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from . import models, schemas


# ✅ Crear un usuario nuevo
def crear_usuario(db: Session, usuario: schemas.UsuarioCreate):
    nuevo_usuario = models.User(name=usuario.name, email=usuario.email)
    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        print(f"[✅ USUARIO CREADO] {nuevo_usuario.email}")
        return nuevo_usuario
    except IntegrityError:
        db.rollback()
        print(f"[⚠️ ERROR] Email duplicado: {usuario.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado en la base de datos."
        )


# ✅ Obtener todos los usuarios
def obtener_usuarios(db: Session):
    return db.query(models.User).all()


# ✅ Borrar un usuario por ID
def borrar_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.User).filter(models.User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    db.delete(usuario)
    db.commit()
    print(f"[🗑️ USUARIO ELIMINADO] ID: {usuario_id}")
    return {"mensaje": "Usuario eliminado correctamente."}
