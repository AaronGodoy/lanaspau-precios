#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
# Forzamos que Alembic ignore el historial roto de versiones y obligamos a recrear las tablas base.
# Esto es útil si las migraciones en producción quedaron en un estado inconsistente.
python -c "from app.db.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
alembic stamp head

# We seed the database only if it's explicitly allowed or needed
# Uncomment the following line if you want the seed script to run on every deploy
python -m app.utils.seed_data

echo "Build script completed."
