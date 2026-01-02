import os

init_db_path = os.path.join("backend", "app", "crud", "init_db.py")

# Correct logic with the adjusted import path
init_db_corrected = """
from sqlalchemy.orm import Session
from ..models import template as models
# CORRECTION: The seed file is in 'core', not 'crud'. 
# We use '..' to go up to 'app', then down into 'core'.
from ..core.seed_data import PERMANENT_TEMPLATES

def sync_templates(db: Session):
    print("🔄 Checking for missing templates...")
    for data in PERMANENT_TEMPLATES:
        existing = db.query(models.Template).filter(models.Template.id == data["id"]).first()
        if not existing:
            print(f"➕ Auto-Adding missing template: {data['name']}")
            new_t = models.Template(**data)
            db.add(new_t)
        else:
            # Always update content on restart to ensure fixes apply
            existing.html_content = data["html"]
            existing.css_styles = data["css"]
            
    db.commit()
    print("✅ Template Database Synced.")
"""

try:
    with open(init_db_path, "w", encoding="utf-8") as f:
        f.write(init_db_corrected)
    print("✅ FIXED: init_db.py now looks in the correct folder ('..core') for seed data.")
except Exception as e:
    print(f"❌ Error: {e}")