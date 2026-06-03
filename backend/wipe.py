from app.db.database import Base, engine
from sqlalchemy import text

with engine.connect() as con:
    con.execute(text('DROP SCHEMA public CASCADE; CREATE SCHEMA public;'))
    con.commit()

Base.metadata.create_all(bind=engine)
