
from sqlalchemy.orm import Session
from ..models import template as models
from .seed_data import PERMANENT_TEMPLATES

def sync_templates(db: Session):
    print("🔄 Checking for missing templates...")
    for data in PERMANENT_TEMPLATES:
        existing = db.query(models.Template).filter(models.Template.id == data["id"]).first()
        if not existing:
            print(f"➕ Auto-Adding missing template: {data['name']}")
            new_t = models.Template(**data)
            db.add(new_t)
        else:
            # OPTIONAL: Force update code on restart to ensure fixes apply
            existing.html_content = data["html"]
            existing.css_styles = data["css"]
            
    db.commit()
    print("✅ Template Database Synced.")
