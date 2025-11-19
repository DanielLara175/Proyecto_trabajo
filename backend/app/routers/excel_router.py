# backend/app/routers/excel_router.py

from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from typing import List, Dict, Any
from datetime import datetime
from mysql.connector import Error

# Importar configuración de base de datos
from app.database import get_db_connection

router = APIRouter(
    prefix="/api/excel",
    tags=["Excel"]
)

# Cola global para el progreso (se asigna desde main.py)
progress_queue = []

# Almacenamiento temporal de datos cargados
uploaded_data_cache = {}

# ============================================================
# Gestión de conexiones WebSocket
# ============================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_progress(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


# ============================================================
# WebSocket para progreso en tiempo real
# ============================================================
@router.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================
# Función: Validar duplicados en BD
# ============================================================
def check_duplicates_in_db(emails: List[str]) -> Dict[str, Any]:
    """
    Verifica qué emails ya existen en la base de datos
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Crear consulta con placeholders
        placeholders = ', '.join(['%s'] * len(emails))
        query = f"SELECT email FROM users WHERE email IN ({placeholders})"
        
        cursor.execute(query, emails)
        existing = cursor.fetchall()
        
        existing_emails = [row['email'] for row in existing]
        cursor.close()
        
        return {
            "existing_count": len(existing_emails),
            "existing_emails": existing_emails
        }
        
    except Error as e:
        print(f"Error al verificar duplicados: {e}")
        return {"existing_count": 0, "existing_emails": []}


# ============================================================
# Función: Insertar usuarios en BD
# ============================================================
def insert_users_to_db(users_data: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Inserta usuarios en la base de datos
    Retorna cantidad insertada y errores
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inserted = 0
        errors = []
        
        for user in users_data:
            try:
                # CORRECCIÓN: Usar 'name' en lugar de 'main'
                query = "INSERT INTO users (name, email) VALUES (%s, %s)"
                cursor.execute(query, (user['name'], user['email']))
                inserted += 1
            except Error as e:
                errors.append({
                    "email": user['email'],
                    "error": str(e)
                })
        
        conn.commit()
        cursor.close()
        
        return {
            "inserted": inserted,
            "errors": errors
        }
        
    except Error as e:
        print(f"Error al insertar usuarios: {e}")
        raise HTTPException(status_code=500, detail=f"Error en BD: {str(e)}")


# ============================================================
# Endpoint: Subir y validar Excel
# ============================================================
@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    """
    Sube archivo Excel, valida estructura, detecta duplicados en archivo y BD
    """
    try:
        # Validar extensión
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Solo archivos Excel (.xlsx, .xls)")
        
        await manager.send_progress({"stage": "reading", "progress": 10, "message": "Leyendo archivo..."})
        
        # Leer Excel
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        await manager.send_progress({"stage": "validating", "progress": 30, "message": "Validando estructura..."})
        
        # CORRECCIÓN: Validación de columnas requeridas (name y email)
        required_columns = ['name', 'email']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"El Excel debe contener las columnas: {', '.join(required_columns)}"
            )
        
        # Validar que no esté vacío
        if df.empty:
            raise HTTPException(status_code=400, detail="El archivo Excel está vacío")
        
        # Limpiar datos
        df['name'] = df['name'].astype(str).str.strip()
        df['email'] = df['email'].astype(str).str.strip().str.lower()
        
        # Eliminar filas con datos vacíos
        df = df.dropna(subset=['name', 'email'])
        df = df[(df['name'] != '') & (df['email'] != '')]
        
        await manager.send_progress({"stage": "checking", "progress": 50, "message": "Detectando duplicados..."})
        
        # Duplicados dentro del archivo
        file_duplicates = df[df.duplicated(subset=['email'], keep=False)]
        file_duplicate_count = len(file_duplicates)
        
        # Verificar duplicados en base de datos
        emails_to_check = df['email'].tolist()
        db_check = check_duplicates_in_db(emails_to_check)
        
        await manager.send_progress({"stage": "processing", "progress": 70, "message": "Procesando datos..."})
        
        # Convertir a diccionarios
        data_dict = df.to_dict(orient='records')
        
        # Generar ID único
        upload_id = f"upload_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Guardar en caché
        uploaded_data_cache[upload_id] = {
            "data": data_dict,
            "columns": df.columns.tolist(),
            "file_duplicates": file_duplicates.to_dict(orient='records'),
            "db_duplicates": db_check['existing_emails'],
            "original_df": df
        }
        
        await manager.send_progress({"stage": "complete", "progress": 100, "message": "¡Carga completada!"})
        
        return {
            "upload_id": upload_id,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "file_duplicate_count": file_duplicate_count,
            "db_duplicate_count": db_check['existing_count'],
            "file_duplicates": file_duplicates.to_dict(orient='records') if file_duplicate_count > 0 else [],
            "db_duplicates": db_check['existing_emails'],
            "preview": data_dict[:10],
            "statistics": {
                "total_valid": len(df),
                "can_insert": len(df) - len(db_check['existing_emails'])
            }
        }
        
    except Exception as e:
        await manager.send_progress({"stage": "error", "progress": 0, "message": f"Error: {str(e)}"})
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Endpoint: Guardar en base de datos
# ============================================================
@router.post("/save-to-db/{upload_id}")
async def save_to_database(upload_id: str, skip_duplicates: bool = True):
    """
    Guarda los datos del Excel en la base de datos
    skip_duplicates: si es True, omite emails que ya existen en BD
    """
    if upload_id not in uploaded_data_cache:
        raise HTTPException(status_code=404, detail="Datos no encontrados. Recarga el archivo.")
    
    try:
        await manager.send_progress({"stage": "saving", "progress": 20, "message": "Preparando inserción..."})
        
        cache = uploaded_data_cache[upload_id]
        df = cache["original_df"]
        
        # Si skip_duplicates, filtrar emails existentes
        if skip_duplicates:
            existing_emails = cache["db_duplicates"]
            df = df[~df['email'].isin(existing_emails)]
        
        # Eliminar duplicados dentro del archivo también
        df = df.drop_duplicates(subset=['email'])
        
        if df.empty:
            return {
                "message": "No hay datos nuevos para insertar",
                "inserted": 0,
                "errors": []
            }
        
        await manager.send_progress({"stage": "inserting", "progress": 50, "message": f"Insertando {len(df)} registros..."})
        
        # CORRECCIÓN: Preparar datos con 'name' en lugar de 'main'
        users_data = df[['name', 'email']].to_dict(orient='records')
        
        # Insertar en BD
        result = insert_users_to_db(users_data)
        
        await manager.send_progress({"stage": "complete", "progress": 100, "message": "¡Guardado exitoso!"})
        
        return {
            "message": f"Se insertaron {result['inserted']} registros correctamente",
            "inserted": result['inserted'],
            "errors": result['errors']
        }
        
    except Exception as e:
        await manager.send_progress({"stage": "error", "progress": 0, "message": f"Error: {str(e)}"})
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Endpoint: Obtener datos completos
# ============================================================
@router.get("/data/{upload_id}")
async def get_full_data(upload_id: str):
    """Obtiene todos los datos cargados"""
    if upload_id not in uploaded_data_cache:
        raise HTTPException(status_code=404, detail="Datos no encontrados")
    
    cache = uploaded_data_cache[upload_id]
    return {
        "data": cache["data"],
        "columns": cache["columns"],
        "total_rows": len(cache["data"])
    }


# ============================================================
# Endpoint: Eliminar duplicados del archivo
# ============================================================
@router.post("/remove-duplicates/{upload_id}")
async def remove_duplicates(upload_id: str):
    """Elimina duplicados dentro del archivo Excel"""
    if upload_id not in uploaded_data_cache:
        raise HTTPException(status_code=404, detail="Datos no encontrados")
    
    cache = uploaded_data_cache[upload_id]
    df = cache["original_df"]
    
    original_count = len(df)
    df_clean = df.drop_duplicates(subset=['email'])
    removed_count = original_count - len(df_clean)
    
    # Actualizar caché
    uploaded_data_cache[upload_id]["data"] = df_clean.to_dict(orient='records')
    uploaded_data_cache[upload_id]["original_df"] = df_clean
    uploaded_data_cache[upload_id]["file_duplicates"] = []
    
    return {
        "message": f"Se eliminaron {removed_count} duplicados del archivo",
        "total_rows": len(df_clean),
        "data": df_clean.to_dict(orient='records')
    }


# ============================================================
# Endpoint: Actualizar celda
# ============================================================
@router.put("/update-cell/{upload_id}")
async def update_cell(upload_id: str, row_index: int, column: str, value: Any):
    """Actualiza valor de una celda"""
    if upload_id not in uploaded_data_cache:
        raise HTTPException(status_code=404, detail="Datos no encontrados")
    
    cache = uploaded_data_cache[upload_id]
    df = cache["original_df"]
    
    if row_index >= len(df) or column not in df.columns:
        raise HTTPException(status_code=400, detail="Índice inválido")
    
    df.at[row_index, column] = value
    
    # Actualizar caché
    uploaded_data_cache[upload_id]["data"] = df.to_dict(orient='records')
    uploaded_data_cache[upload_id]["original_df"] = df
    
    return {"message": "Actualizado", "updated_value": value}


# ============================================================
# Endpoint: Estadísticas para gráficos
# ============================================================
@router.get("/statistics/{upload_id}")
async def get_statistics(upload_id: str):
    """Genera estadísticas para gráficos"""
    if upload_id not in uploaded_data_cache:
        raise HTTPException(status_code=404, detail="Datos no encontrados")
    
    cache = uploaded_data_cache[upload_id]
    df = cache["original_df"]
    
    # Gráfico de Torta: Dominios de email más comunes
    df['domain'] = df['email'].str.split('@').str[1]
    domain_counts = df['domain'].value_counts().head(5)
    
    pie_data = {
        "labels": domain_counts.index.tolist(),
        "values": domain_counts.values.tolist(),
        "column": "Dominios de Email"
    }
    
    # CORRECCIÓN: Gráfico de Barras usando 'name' en lugar de 'main'
    bar_data = {
        "labels": df['name'].head(10).tolist(),
        "values": list(range(1, min(11, len(df) + 1))),
        "column": "Usuarios"
    }
    
    return {
        "pie_chart": pie_data,
        "bar_chart": bar_data,
        "total_rows": len(df),
        "total_columns": len(df.columns)
    }


# ============================================================
# Endpoint: Exportar Excel
# ============================================================
@router.get("/export/{upload_id}")
async def export_excel(upload_id: str):
    """Exporta Excel modificado"""
    if upload_id not in uploaded_data_cache:
        raise HTTPException(status_code=404, detail="Datos no encontrados")
    
    cache = uploaded_data_cache[upload_id]
    df = cache["original_df"]
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Usuarios')
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=usuarios_modificados.xlsx"}
    )