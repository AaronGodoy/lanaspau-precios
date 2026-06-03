#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running database initialization..."
# Forzamos que se eliminen y creen todas las tablas para solucionar inconsistencias de migraciones en producción
python reset_db.py

# Marcar las migraciones como actualizadas para que alembic no intente correrlas
alembic stamp head

echo "Build script completed."
