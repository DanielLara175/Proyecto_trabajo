FROM python:3.11

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todo el backend al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando por defecto al iniciar el contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
