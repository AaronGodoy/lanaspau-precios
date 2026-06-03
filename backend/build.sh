#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
alembic upgrade head

# We seed the database only if it's explicitly allowed or needed
# Uncomment the following line if you want the seed script to run on every deploy
python -m app.utils.seed_data

echo "Build script completed."
