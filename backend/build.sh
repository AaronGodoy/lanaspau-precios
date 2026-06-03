#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database initialization..."
# Ya no forzamos el reseteo porque estamos en etapa de produccion.
# python reset_db.py

echo "Running migrations..."
alembic upgrade head

# Marcar las migraciones como actualizadas para que alembic no intente correrlas si no hay nuevas
# alembic stamp head

echo "Build script completed."
