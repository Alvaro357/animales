# Dockerfile para Django - Asociaciones de Animales
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Crear directorio para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/media

# Recoger archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "mysite.wsgi:application"]
