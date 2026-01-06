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
# Replace the normalize_cv_dict function in main_api.py with this version

def normalize_cv_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts incoming React JSON (camelCase) to Schema-Compliant (snake_case)
    dictionary that matches the 'CVData' Pydantic model structure.
    NOW WITH CUSTOM FIELDS SUPPORT!
    """
    normalized: Dict[str, Any] = {}

    # 1. Key Mapping (React -> Schema)
    key_map = {
        # Basic Fields
        "fullName": "full_name",
        "jobTitle": "job_title",
        "phone": "phone",
        "email": "email",
        "summary": "summary",
        "experience": "experience",
        "education": "education",
        "skills": "skills",
        
        # NEW: Custom Sidebar Fields
        "location": "location",
        "hobbies": "hobbies",
        "languages": "languages",
        "certifications": "certifications",
        
        # NEW: Social Links
        "linkedin": "linkedin",
        "github": "github",
        "portfolio": "portfolio"
    }

    # Transfer existing keys
    for k, v in data.items():
        if k in key_map:
            normalized[key_map[k]] = v
        elif k in key_map.values():
            normalized[k] = v
        elif k in ["accentColor", "textColor", "fontFamily"]:
            normalized[k] = v

    # 2. Strict Defaults for Required Fields
    required_str_fields = ["full_name", "email", "phone", "job_title", "summary", "experience", "education"]
    for field in required_str_fields:
        if field not in normalized or normalized[field] is None:
            normalized[field] = ""
    
    # 3. Handle Skills List
    skills_raw = normalized.get("skills")
    if isinstance(skills_raw, str):
        if skills_raw.strip():
            normalized["skills"] = [s.strip() for s in skills_raw.split(',') if s.strip()]
        else:
            normalized["skills"] = []
    elif not isinstance(skills_raw, list):
        normalized["skills"] = []

    # 4. NEW: Handle Custom Lists (Hobbies, Languages, Certifications)
    for list_field in ["hobbies", "languages", "certifications"]:
        field_raw = normalized.get(list_field)
        if isinstance(field_raw, str):
            if field_raw.strip():
                normalized[list_field] = [s.strip() for s in field_raw.split(',') if s.strip()]
            else:
                normalized[list_field] = []
        elif not isinstance(field_raw, list):
            normalized[list_field] = []

    # 5. NEW: Handle Optional String Fields
    for str_field in ["location", "linkedin", "github", "portfolio"]:
        if str_field not in normalized or normalized[str_field] is None:
            normalized[str_field] = ""

    # 6. Generate Initials
    name = normalized.get("full_name", "")
    normalized["full_name_initials"] = name[:2].upper() if name else "??"

    # 7. Fix Accent Colors
    if "accentColor" in normalized: normalized["accent_color"] = normalized["accentColor"]
    if "textColor" in normalized: normalized["text_color"] = normalized["textColor"]
    if "fontFamily" in normalized: normalized["font_family"] = normalized["fontFamily"]
    
    normalized.setdefault("accent_color", "#2c3e50")
    normalized.setdefault("text_color", "#333333")
    
    return normalized

def render_template_internal(html_content: str, css_content: str, data: Dict[str, Any]) -> str:
    """
    Safe Internal Rendering of HTML using Jinja2.
    Templates have #{{accent_color}} syntax, so we provide colors WITHOUT #.
    """
    mapped_data = normalize_cv_dict(data)
    
    def strip_hash(color):
        if not color:
            return "333333"
        clean = str(color).replace("#", "")
        if re.fullmatch(r"[0-9a-fA-F]{3}|[0-9a-fA-F]{6}", clean):
            if len(clean) == 3:
                clean = ''.join([c*2 for c in clean])
            return clean
        return "333333"
    
    if "accent_color" in mapped_data:
        mapped_data["accent_color"] = strip_hash(mapped_data["accent_color"])
    if "text_color" in mapped_data:
        mapped_data["text_color"] = strip_hash(mapped_data["text_color"])
    
    env = jinja2.Environment(loader=jinja2.BaseLoader())
    
    clean_html = html_content.replace("{{{", "{{").replace("}}}", " | safe }}")
    clean_css = css_content.replace("{{{", "{{").replace("}}}", " | safe }}")
    
    try:
        t_html = env.from_string(clean_html)
        t_css = env.from_string(clean_css or "")
        
        rendered_body = t_html.render(**mapped_data)
        rendered_css = t_css.render(**mapped_data)
        
        # CSS Cleanup
        rendered_css = re.sub(r'##+', '#', rendered_css)
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
    token = security.create_jwt_token({"user_id": new_user.id, "email": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/auth/login", response_model=user_schemas.Token)
def login(user: user_schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user.email)
    if not db_user or not security.verify_password(user.password, str(db_user.password_hash)): 
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = security.create_jwt_token({"user_id": db_user.id, "email": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/auth/profile", response_model=user_schemas.User)
def profile(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_crud.get_user(db, int(user["user_id"]))

# ---------------------------------------------------------
# AI ENDPOINTS
# ---------------------------------------------------------
@router.post("/ai/chat")
async def chat_endpoint(req: dict, user: dict = Depends(get_current_user)):
    history = [{"role": m['role'], "content": m['content']} for m in req.get('history', [])]
    response = ai_service.chat_with_user(history, req.get('message', ''))
    
    if response["action"] == "generate":
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
    clean_dict = normalize_cv_dict(raw_data)
    
    try:
        cv_data_obj = cv_schemas.CVData(**clean_dict)
    except Exception as e:
        logger.error(f"Validation Error: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid Data Structure: {str(e)}")

    cv_in = cv_schemas.CVCreate(
        title=payload.get("title", "My New CV"),
        template_id=payload.get("template_id", "modern"),
        data=cv_data_obj
    )
    
    user_id = int(user["user_id"])
    return cv_crud.create_cv(db, cv_in, user_id)

@router.get("/cvs", response_model=List[cv_schemas.CVInDB])
def list_cvs_endpoint(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return cv_crud.get_all_user_cvs(db, int(user["user_id"]))

@router.get("/cvs/{cv_id}/export/{type}")
def export_endpoint(cv_id: int, type: str, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db_cv = cv_crud.get_cv(db, int(cv_id), int(user["user_id"]))
    if not db_cv:
        raise HTTPException(404, "CV not found")

    data_source = db_cv.data
    if hasattr(data_source, "model_dump"):
        cv_dict = data_source.model_dump()
    elif hasattr(data_source, "dict"):
        cv_dict = data_source.dict()
    else:
        cv_dict = dict(data_source) # type: ignore

    template_id_str = str(db_cv.template_id)
    tmpl = template_crud.get_template(db, template_id_str)
    if not tmpl: 
        tmpl = template_crud.get_template(db, "modern")

    if not tmpl: raise HTTPException(404, "Default Template missing")

    if type == 'pdf':
        pdf_bytes = file_service.create_pdf_from_template(tmpl.html_content, tmpl.css_styles, cv_dict)
        return Response(content=pdf_bytes, media_type="application/pdf")
            
    elif type == 'html':
        full_html = render_template_internal(tmpl.html_content, tmpl.css_styles, cv_dict)
        return Response(content=full_html, media_type="text/html")
        
    elif type == 'docx':
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
    Direct Preview endpoint for frontend live preview.
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
# TEMPLATE ENDPOINTS
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
        update_data = template_schemas.TemplateUpdate(
            name=t.name,
            category=t.category,
            is_premium=t.is_premium,
            html_content=t.html_content,
            css_styles=t.css_styles
        )
        return template_crud.update_template(db, exist, update_data)
    
    return template_crud.create_template(db, t)

# ---------------------------------------------------------
# SETUP ENDPOINT (Keep for template syncing)
# ---------------------------------------------------------
@router.get("/setup_production")
def setup_production_db(db: Session = Depends(get_db)):
    """
    Syncs templates from seed_data.py to database.
    Use after deploying template updates.
    """
    from .models.template import Template
    from .core.seed_data import PERMANENT_TEMPLATES
    
    deleted_count = db.query(Template).delete()
    db.commit()
    
    added_count = 0
    for data in PERMANENT_TEMPLATES:
        new_t = Template(**data)
        db.add(new_t)
        added_count += 1
    
    db.commit()
    
    return {
        "status": "success",
        "deleted": deleted_count,
        "added": added_count,
        "message": f"Database synced: {deleted_count} removed, {added_count} added from seed_data.py"
    }