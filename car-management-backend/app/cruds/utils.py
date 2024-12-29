from fastapi import HTTPException
from sqlalchemy.orm import Session


def get_or_404(db: Session, model, obj_id: int, detail: str):
    """Retrieve an object or raise 404 if not found."""
    obj = db.query(model).filter(model.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=detail)
    return obj


def update_relationship(db: Session, obj, relationship_attr, related_model, related_ids):
    """Update many-to-many relationships for a given object."""
    related_objects = db.query(related_model).filter(related_model.id.in_(related_ids)).all()
    setattr(obj, relationship_attr, related_objects)
