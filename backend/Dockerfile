FROM python:3.10

WORKDIR /app

# Copiar requirements primero
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el backend (incluye la carpeta app/)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
