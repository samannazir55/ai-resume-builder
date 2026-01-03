from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Response
from typing import List, Dict, Any, Union
from sqlalchemy.orm import Session
import jinja2
import logging
import re

# Check for WeasyPrint
try:
    from weasyprint import HTML, CSS # type: ignore
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

# Local Imports
from .database import get_db
from .schemas import user as user_schemas, cv as cv_schemas, ai as ai_schemas, template as template_schemas
from .crud import user as user_crud, cv as cv_crud, template as template_crud
from .core import security, config
from .services import ai_service, parser_service, file_service
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
bearer = HTTPBearer()
logger = logging.getLogger("cv_api")

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    return security.verify_jwt_token(creds.credentials)

# ---------------------------------------------------------
# DATA NORMALIZER (Fixes Validation Errors)
# ---------------------------------------------------------
def normalize_cv_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts incoming React JSON (camelCase) to Schema-Compliant (snake_case)
    dictionary that matches the 'CVData' Pydantic model structure.
    """
    normalized: Dict[str, Any] = {}

    # 1. Key Mapping (React -> Schema)
    key_map = {
        "fullName": "full_name",
        "jobTitle": "job_title",
        "phone": "phone",
        "email": "email",
        "summary": "summary",
        "experience": "experience", # Handles both String (Editor) or List
        "education": "education",
        "skills": "skills",
        "languages": "languages",
        "certifications": "certifications"
    }

    # Transfer existing keys (keeping existing snake_case if present)
    for k, v in data.items():
        if k in key_map:
            normalized[key_map[k]] = v
        # Also keep keys that are already snake_case (like full_name)
        elif k in key_map.values():
            normalized[k] = v
        # Keep styling preferences
        elif k in ["accentColor", "textColor", "fontFamily"]:
            normalized[k] = v

    # 2. Strict Defaults (Required by schemas.CVData)
    # The Schema requires these fields to be strings, not None
    required_str_fields = ["full_name", "email", "phone", "job_title", "summary", "experience", "education"]
    for field in required_str_fields:
        if field not in normalized or normalized[field] is None:
            normalized[field] = ""
    
    # 3. Handle Lists (Skills)
    # Schema requires List[str], React might send "Skill1, Skill2" string
    skills_raw = normalized.get("skills")
    if isinstance(skills_raw, str):
        if skills_raw.strip():
            normalized["skills"] = [s.strip() for s in skills_raw.split(',') if s.strip()]
        else:
            normalized["skills"] = []
    elif not isinstance(skills_raw, list):
        normalized["skills"] = []

    # 4. Generate Initials (for Placeholder Avatar)
    name = normalized.get("full_name", "")
    normalized["full_name_initials"] = name[:2].upper() if name else "??"

    # 5. Fix Accent Colors (Map camelCase to snake_case for Template Engine)
    if "accentColor" in normalized: normalized["accent_color"] = normalized["accentColor"]
    if "textColor" in normalized: normalized["text_color"] = normalized["textColor"]
    if "fontFamily" in normalized: normalized["font_family"] = normalized["fontFamily"]
    
    # Fallback Defaults for Template Colors
    normalized.setdefault("accent_color", "#2c3e50")
    normalized.setdefault("text_color", "#333333")
    
    return normalized

def render_template_internal(html_content: str, css_content: str, data: Dict[str, Any]) -> str:
    """
    Safe Internal Rendering of HTML using Jinja2.
    
    CRITICAL: This function provides colors WITHOUT # prefix because
    the templates have #{{accent_color}} syntax built-in.
    """
    mapped_data = normalize_cv_dict(data)
    
    # CRITICAL FIX: Remove hash from colors - templates add it via #{{color}}
    def strip_hash(color):
        if not color:
            return "333333"
        clean = str(color).replace("#", "")
        # Validate it's actually hex
        if re.fullmatch(r"[0-9a-fA-F]{3}|[0-9a-fA-F]{6}", clean):
            # Expand 3-char to 6-char if needed
            if len(clean) == 3:
                clean = ''.join([c*2 for c in clean])
            return clean
        return "333333"
    
    # Ensure colors are WITHOUT hash for templates that use #{{color}}
    if "accent_color" in mapped_data:
        mapped_data["accent_color"] = strip_hash(mapped_data["accent_color"])
    if "text_color" in mapped_data:
        mapped_data["text_color"] = strip_hash(mapped_data["text_color"])
    
    env = jinja2.Environment(loader=jinja2.BaseLoader())
    
    # Convert Mustache syntax to Jinja2
    clean_html = html_content.replace("{{{", "{{").replace("}}}", " | safe }}")
    clean_css = css_content.replace("{{{", "{{").replace("}}}", " | safe }}")
    
    try:
        t_html = env.from_string(clean_html)
        t_css = env.from_string(clean_css or "")
        
        rendered_body = t_html.render(**mapped_data)
        rendered_css = t_css.render(**mapped_data)
        
        # CLEANUP: Fix any double hashes that might have been created
        rendered_css = re.sub(r'##+', '#', rendered_css)
        # Fix orphaned hashes
        rendered_css = re.sub(r':\s*#\s*;', ': #333333;', rendered_css)
        rendered_css = re.sub(r':\s*#\s*\}', ': #333333', rendered_css)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {rendered_css}
                body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; margin: 0; }}
            </style>
        </head>
        <body>
            {rendered_body}
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"Render Error: {e}")
        return f"<h1>Error generating preview</h1><pre>{e}</pre>"


# ---------------------------------------------------------
# AUTH ENDPOINTS
# ---------------------------------------------------------
@router.post("/auth/register", response_model=user_schemas.Token)
def register(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = user_crud.create_user(db, user)
    # Ensure ID is treated as int/str properly
    token = security.create_jwt_token({"user_id": new_user.id, "email": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/login", response_model=user_schemas.Token)
def login(user: user_schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user.email)
    # Cast password_hash to str to satisfy Pylance
    if not db_user or not security.verify_password(user.password, str(db_user.password_hash)): 
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = security.create_jwt_token({"user_id": db_user.id, "email": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/auth/profile", response_model=user_schemas.User)
def profile(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Assuming user["user_id"] is int
    return user_crud.get_user(db, int(user["user_id"]))

# ---------------------------------------------------------
# AI ENDPOINTS
# ---------------------------------------------------------
@router.post("/ai/chat")
async def chat_endpoint(req: dict, user: dict = Depends(get_current_user)):
    history = [{"role": m['role'], "content": m['content']} for m in req.get('history', [])]
    response = ai_service.chat_with_user(history, req.get('message', ''))
    
    if response["action"] == "generate":
        # Create strict schema for AI generation
        req_data = response["data"]
        gen_req = ai_schemas.AIGenerationRequest(
            full_name=req_data.get("full_name", "User"),
            email=user.get("email", ""),
            desired_job_title=req_data.get("desired_job_title", ""),
            top_skills=req_data.get("top_skills", []),
            experience_level=req_data.get("experience_level", ""),
            personal_strengths=req_data.get("professional_summary", "")
        )
        cv_data = ai_service.generate_cv_content_from_ai(gen_req)
        if cv_data.success:
            return {"reply": response["reply"], "action": "generate", "cv_data": cv_data.data}
            
    return response

@router.post("/ai/upload-resume")
async def upload_endpoint(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    content = await file.read()
    # Pylance: Ensure filename is str
    fname = str(file.filename) if file.filename else "resume.pdf"
    text = parser_service.extract_text(content, fname)
    return {"success": True, "extracted_text": text}

# ---------------------------------------------------------
# CV ENDPOINTS
# ---------------------------------------------------------
@router.post("/cvs")
def create_cv_endpoint(payload: Dict[str, Any], db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    """
    Creates a new CV. Accepts a raw Dict to allow backend normalizer to
    convert CamelCase -> SnakeCase BEFORE strictly validating against CVData schema.
    """
    raw_data = payload.get("data", {})
    # 1. Clean data to match 'schemas/cv.py' expectations
    clean_dict = normalize_cv_dict(raw_data)
    
    # 2. Convert to strict CVData object
    try:
        cv_data_obj = cv_schemas.CVData(**clean_dict)
    except Exception as e:
        logger.error(f"Validation Error: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid Data Structure: {str(e)}")

    # 3. Create wrapper schema
    cv_in = cv_schemas.CVCreate(
        title=payload.get("title", "My New CV"),
        template_id=payload.get("template_id", "modern"),
        data=cv_data_obj
    )
    
    # 4. Save to DB
    user_id = int(user["user_id"])
    return cv_crud.create_cv(db, cv_in, user_id)

@router.get("/cvs", response_model=List[cv_schemas.CVInDB])
def list_cvs_endpoint(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return cv_crud.get_all_user_cvs(db, int(user["user_id"]))

@router.get("/cvs/{cv_id}/export/{type}")
def export_endpoint(cv_id: int, type: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    # 1. Fetch CV (with correct ID type)
    db_cv = cv_crud.get_cv(db, int(cv_id), int(user["user_id"]))
    if not db_cv:
        raise HTTPException(404, "CV not found")

    # 2. Get Data (Handle SQL column types safely)
    # Convert 'CVData' object to Dict if it's stored as an object, or use it directly
    data_source = db_cv.data
    # If using Pydantic V2 model dump:
    if hasattr(data_source, "model_dump"):
        cv_dict = data_source.model_dump()
    elif hasattr(data_source, "dict"):
        cv_dict = data_source.dict()
    else:
        # Fallback if stored as plain JSON in DB
        cv_dict = dict(data_source) # type: ignore

    # 3. Get Template
    # explicit str() cast to safely query by ID
    template_id_str = str(db_cv.template_id)
    tmpl = template_crud.get_template(db, template_id_str)
    # Fallback to modern
    if not tmpl: 
        tmpl = template_crud.get_template(db, "modern")

    if not tmpl: raise HTTPException(404, "Default Template missing")

    # 4. Generate Output
    if type == 'pdf':
        # Use file_service for PDF generation (it uses pystache)
        pdf_bytes = file_service.create_pdf_from_template(tmpl.html_content, tmpl.css_styles, cv_dict)
        return Response(content=pdf_bytes, media_type="application/pdf")
            
    elif type == 'html':
        full_html = render_template_internal(tmpl.html_content, tmpl.css_styles, cv_dict)
        return Response(content=full_html, media_type="text/html")
        
    elif type == 'docx':
        # Clean dict for Docx service
        clean_docx_data = normalize_cv_dict(cv_dict)
        docx_bytes = file_service.create_docx_from_data(clean_docx_data)
        filename = "resume.docx"
        return Response(
            content=docx_bytes, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    raise HTTPException(400, "Unknown format")

@router.post("/generate-pdf")
def generate_pdf_direct(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Direct Preview endpoint.
    Accepts generic JSON, fixes keys, and returns HTML.
    """
    raw_data = payload.get("data", {})
    t_id = payload.get("template_id", "modern")
    
    tmpl = template_crud.get_template(db, str(t_id))
    if not tmpl: 
        tmpl = template_crud.get_template(db, "modern")

    if tmpl:
        full_html = render_template_internal(tmpl.html_content, tmpl.css_styles, raw_data)
        return Response(content=full_html, media_type="text/html")
    
    return Response(content="<h1>Template Error</h1>", media_type="text/html")

# ---------------------------------------------------------
# TEMPLATES ADMIN
# ---------------------------------------------------------
@router.get("/templates", response_model=List[template_schemas.Template])
def get_templates(db: Session = Depends(get_db)):
    return template_crud.get_all_templates(db)

@router.get("/templates/{id}", response_model=template_schemas.TemplateFull)
def get_single_template(id: str, db: Session = Depends(get_db)):
    t = template_crud.get_template(db, id)
    if not t: raise HTTPException(404, "Template not found")
    return t

@router.post("/admin/templates", response_model=template_schemas.Template)
def admin_create(t: template_schemas.TemplateCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user.get("email") != config.settings.ADMIN_EMAIL: 
        raise HTTPException(403, "Admin Access Required")
    
    exist = template_crud.get_template(db, t.id)
    if exist:
        # STRICT TYPE FIX: Convert 'TemplateCreate' -> 'TemplateUpdate'
        # to satisfy Pylance assignment rules
        update_data = template_schemas.TemplateUpdate(
            name=t.name,
            category=t.category,
            is_premium=t.is_premium,
            html_content=t.html_content,
            css_styles=t.css_styles
        )
        return template_crud.update_template(db, exist, update_data)
    
    return template_crud.create_template(db, t)

# ==========================================
# ⚡ PRODUCTION SETUP ROUTE - FIXED VERSION
# This now imports from seed_data.py
# ==========================================
@router.get("/setup_production")
def setup_production_db(db: Session = Depends(get_db)):
    """
    UPDATED: Imports templates from seed_data.py and syncs to Neon database.
    Call this after deploying new template fixes.
    """
    from .models.template import Template
    from .core.seed_data import PERMANENT_TEMPLATES
    
    # 1. Delete ALL existing templates (nuclear option)
    deleted_count = db.query(Template).delete()
    db.commit()
    logger.info(f"🗑️  Deleted {deleted_count} old templates from Neon")
    
    # 2. Add fresh templates from seed_data.py
    added_count = 0
    for data in PERMANENT_TEMPLATES:
        logger.info(f"➕ Adding template: {data['name']}")
        new_t = Template(**data)
        db.add(new_t)
        added_count += 1
    
    db.commit()
    logger.info(f"✅ Added {added_count} fresh templates to Neon")
    
    return {
        "status": "success",
        "deleted": deleted_count,
        "added": added_count,
        "message": f"Neon DB Updated: Deleted {deleted_count} old templates, added {added_count} new ones from seed_data.py"
    }

@router.get("/admin/show_template/{template_id}")
def show_template_css(template_id: str, db: Session = Depends(get_db)):
    """
    Shows the FULL CSS of a template to debug
    """
    from .models.template import Template
    
    t = db.query(Template).filter(Template.id == template_id).first()
    
    if not t:
        return {"error": "Template not found"}
    
    return {
        "id": t.id,
        "name": t.name,
        "full_css": t.css_styles,
        "has_mustache_vars": "{{accent_color}}" in t.css_styles,
        "has_hash_prefix": "#{{accent_color}}" in t.css_styles,
        "character_81": t.css_styles[81] if len(t.css_styles) > 81 else "N/A",
        "chars_70_90": t.css_styles[70:90] if len(t.css_styles) > 90 else "N/A"
    }

@router.get("/admin/debug_render/{template_id}")
def debug_render(template_id: str, db: Session = Depends(get_db)):
    """
    Shows what the CSS looks like AFTER rendering with sample data
    """
    from .models.template import Template
    import jinja2
    
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        return {"error": "Template not found"}
    
    # Sample data (colors WITHOUT # - templates add it)
    test_data = {
        "accent_color": "2c3e50",
        "text_color": "333333",
        "font_family": "sans-serif"
    }
    
    # Render it
    env = jinja2.Environment(loader=jinja2.BaseLoader())
    template = env.from_string(t.css_styles)
    rendered_css = template.render(**test_data)
    
    return {
        "template_id": template_id,
        "original_css": t.css_styles[:200],
        "rendered_css": rendered_css[:500],
        "char_81": rendered_css[81] if len(rendered_css) > 81 else "N/A",
        "chars_70_90": rendered_css[70:90] if len(rendered_css) > 90 else "N/A"
    }