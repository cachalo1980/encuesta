FROM python:3.11-slim-bullseye

# Evita que Python genere archivos .pyc y que bufferice stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiamos primero requirements.txt para aprovechar la caché de capas de Docker:
# si el código cambia pero las dependencias no, Docker reutiliza la capa de pip install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
