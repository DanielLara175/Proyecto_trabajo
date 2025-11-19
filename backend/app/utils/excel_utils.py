import pandas as pd
from sqlalchemy.orm import Session
from app.models import User
from io import BytesIO

# ==========================================================
# Función para cargar datos desde un archivo Excel (.xlsx)
# ==========================================================
def load_excel_to_db(file, db: Session):
    """
    Lee un archivo Excel y guarda los datos en la tabla 'users'.

    Args:
        file (UploadFile.file): Archivo Excel subido por el usuario.
        db (Session): Sesión activa de SQLAlchemy para la BD.
    """
    try:
        # ============================================
        # Leer bytes del archivo para evitar errores de seekable
        # ============================================
        file_bytes = file.read()

        # Convertir a un buffer compatible con pandas
        excel_buffer = BytesIO(file_bytes)

        # Leer el Excel con pandas
        df = pd.read_excel(excel_buffer)

        # ============================================
        # Validar columnas
        # ============================================
        expected_columns = {"name", "email"}
        if not expected_columns.issubset(df.columns):
            raise ValueError(f"El archivo Excel debe contener las columnas: {expected_columns}")

        # ============================================
        # Insertar datos
        # ============================================
        for _, row in df.iterrows():
            user = User(
                name=row["name"],
                email=row["email"]
            )
            db.add(user)

        db.commit()
        print("Datos importados correctamente desde el Excel.")
        return {"message": f"Se importaron {len(df)} usuarios correctamente."}

    except Exception as e:
        db.rollback()
        print(f"Error al importar datos: {e}")
        raise e
