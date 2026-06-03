from sqlalchemy.orm import Session
from app.db.models import ChangeHistory

def log_change(db: Session, usuario_id: int | None, entidad: str, entidad_id: int, accion: str, detalle: str) -> None:
    db.add(ChangeHistory(usuario_id=usuario_id, entidad=entidad, entidad_id=entidad_id, accion=accion, detalle=detalle))
