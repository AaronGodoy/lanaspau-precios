import os
import sys

# Añadir el directorio actual al path para que Python encuentre 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import Base, engine
from app.utils.seed_data import run as seed_db
import sqlalchemy as sa

def reset_db():
    print("Iniciando reseteo de base de datos de producción...")
    
    # 1. Eliminar todas las tablas si existen
    print("Eliminando tablas existentes...")
    Base.metadata.drop_all(bind=engine)
    
    # 2. Borrar la tabla de versiones de alembic si existe
    with engine.connect() as conn:
        conn.execute(sa.text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        conn.commit()
    
    # 3. Crear todas las tablas desde cero usando los modelos actuales
    print("Creando tablas con el esquema más reciente...")
    Base.metadata.create_all(bind=engine)
    
    # 4. Sembrar los datos (usuario admin)
    print("Insertando datos iniciales...")
    seed_db()
    
    print("Reseteo y carga de base de datos completada exitosamente.")

if __name__ == "__main__":
    reset_db()
