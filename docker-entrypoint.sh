#!/bin/bash
set -e

echo "========================================"
echo "Iniciando Django con Sistema de Cache"
echo "========================================"

# Esperar a que PostgreSQL esté listo
echo "Esperando PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL está listo!"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Crear tabla de caché (ignora si ya existe)
echo "Creando tabla de caché..."
python manage.py createcachetable || true

# Recoger archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "========================================"
echo "Iniciando servidor..."
echo "Sistema de caché ACTIVO"
echo "========================================"

# Ejecutar el comando pasado al contenedor
exec "$@"
