from sqlalchemy.orm import Session
from ..models import template as models
from ..schemas import template as schemas

def get_template(db: Session, template_id: str):
    return db.query(models.Template).filter(models.Template.id == template_id).first()

def get_all_templates(db: Session):
    return db.query(models.Template).all()

def create_template(db: Session, template: schemas.TemplateCreate):
    # FIX IS HERE: Convert Pydantic model to Dict before saving
    # We try model_dump() first (Pydantic V2), then dict() (V1 fallback)
    if hasattr(template, "model_dump"):
        data = template.model_dump()
    else:
        data = template.dict()
        
    db_obj = models.Template(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_template(db: Session, db_obj: models.Template, obj_in: schemas.TemplateUpdate):
    # Convert input to dict, excluding unset fields so we don't wipe data
    if hasattr(obj_in, "model_dump"):
        update_data = obj_in.model_dump(exclude_unset=True)
    else:
        update_data = obj_in.dict(exclude_unset=True)
        
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
            
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_template(db: Session, template_id: str):
    db_obj = get_template(db, template_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return True
    return False

# Necessary stub to prevent startup errors if main.py calls it
def populate_default_templates(db: Session):
    # Logic is now handled via Admin Panel or injection scripts
    # We keep this as a pass-through to ensure Main.py doesn't crash on import
    pass
