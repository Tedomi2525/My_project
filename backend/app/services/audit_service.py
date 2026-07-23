from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    @staticmethod
    def log(db: Session, actor, action: str, entity_type: str, entity_id=None, details=None):
        item = AuditLog(
            actor_role=actor.role,
            actor_id=actor.id,
            actor_name=getattr(actor, "full_name", None),
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            details=details or {},
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
