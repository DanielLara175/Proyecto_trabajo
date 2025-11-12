# esta parte es ecencial y nos ayuda y aqui ajustamos los modelos de datos entrada y salida post,get, delete

# app/schemas.py
from pydantic import BaseModel, EmailStr

# ✅ Esquema para crear un usuario (entrada)
class UsuarioCreate(BaseModel):
    name: str
    email: EmailStr  # Usa EmailStr para validar formato de correo automáticamente

# ✅ Esquema para leer/retornar un usuario (respuesta)
class UsuarioRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    # Configuración para convertir automáticamente modelos ORM de SQLAlchemy a Pydantic
    class Config:
        from_attributes = True  # Reemplaza orm_mode=True en Pydantic v2
