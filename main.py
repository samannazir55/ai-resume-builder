from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import sqlite3
import jwt
import hashlib
import datetime
import json
import os
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
from docx.shared import Inches
import uuid
import asyncio
from contextlib import asynccontextmanager

# Global variables for AI model
tokenizer = None
model = None
cv_generator = None

# Database setup
def init_db():
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            subscription_plan TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    # CVs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            data JSON NOT NULL,
            template_id TEXT DEFAULT 'modern',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            is_premium BOOLEAN DEFAULT 0,
            html_content TEXT NOT NULL,
            css_styles TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Initialize AI model
async def load_ai_model():
    global tokenizer, model, cv_generator
    try:
        print("Loading AI model...")
        # Use a lightweight model that works well for text generation
        model_name = "microsoft/DialoGPT-small"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)

        # Create text generation pipeline
        cv_generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=100,
            do_sample=True,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )
        print("AI model loaded successfully!")

        # Insert default templates
        insert_default_templates()

    except Exception as e:
        print(f"Error loading AI model: {e}")
        # Fallback to rule-based suggestions
        cv_generator = None

def insert_default_templates():
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    templates = [
        {
            'id': 'modern',
            'name': 'Modern',
            'category': 'professional',
            'is_premium': False,
            'html_content': '''
            <div class="cv-modern">
                <header class="cv-header">
                    <h1>{{full_name}}</h1>
                    <p class="job-title">{{job_title}}</p>
                    <div class="contact-info">
                        <span>{{email}}</span> | <span>{{phone}}</span>
                    </div>
                </header>
                <section class="cv-summary">
                    <h2>Professional Summary</h2>
                    <p>{{summary}}</p>
                </section>
                <section class="cv-experience">
                    <h2>Experience</h2>
                    <div>{{experience}}</div>
                </section>
                <section class="cv-education">
                    <h2>Education</h2>
                    <div>{{education}}</div>
                </section>
                <section class="cv-skills">
                    <h2>Skills</h2>
                    <div class="skills-list">{{skills}}</div>
                </section>
            </div>
            ''',
            'css_styles': '''
            .cv-modern { font-family: 'Segoe UI', sans-serif; color: #333; }
            .cv-header { text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .cv-header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .job-title { font-size: 1.3em; margin-bottom: 10px; }
            .contact-info { font-size: 1em; }
            .cv-summary, .cv-experience, .cv-education, .cv-skills { margin-bottom: 25px; }
            .cv-summary h2, .cv-experience h2, .cv-education h2, .cv-skills h2 { color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 5px; }
            .skills-list { display: flex; flex-wrap: wrap; gap: 10px; }
            '''
        },
        {
            'id': 'classic',
            'name': 'Classic',
            'category': 'traditional',
            'is_premium': False,
            'html_content': '''
            <div class="cv-classic">
                <header class="cv-header">
                    <h1>{{full_name}}</h1>
                    <p>{{job_title}}</p>
                    <p>{{email}} | {{phone}}</p>
                </header>
                <section class="cv-summary">
                    <h2>Objective</h2>
                    <p>{{summary}}</p>
                </section>
                <section class="cv-experience">
                    <h2>Professional Experience</h2>
                    <div>{{experience}}</div>
                </section>
                <section class="cv-education">
                    <h2>Education</h2>
                    <div>{{education}}</div>
                </section>
                <section class="cv-skills">
                    <h2>Core Competencies</h2>
                    <div>{{skills}}</div>
                </section>
            </div>
            ''',
            'css_styles': '''
            .cv-classic { font-family: 'Times New Roman', serif; color: #000; line-height: 1.4; }
            .cv-header { text-align: center; margin-bottom: 25px; border-bottom: 2px solid #000; padding-bottom: 15px; }
            .cv-header h1 { font-size: 2.2em; margin-bottom: 8px; }
            .cv-summary h2, .cv-experience h2, .cv-education h2, .cv-skills h2 { font-size: 1.1em; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #000; }
            '''
        }
    ]

    for template in templates:
        cursor.execute('''
            INSERT OR REPLACE INTO templates (id, name, category, is_premium, html_content, css_styles)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (template['id'], template['name'], template['category'], template['is_premium'], 
              template['html_content'], template['css_styles']))

    conn.commit()
    conn.close()

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    await load_ai_model()
    yield
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="AI CV Builder API",
    description="Self-hosted AI-powered CV Builder with custom trained models",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CVCreate(BaseModel):
    title: str
    full_name: str
    email: str
    phone: str
    job_title: str
    summary: str
    experience: str
    education: str
    skills: List[str]
    languages: str
    certifications: str
    template_id: str = "modern"

class CVUpdate(BaseModel):
    title: Optional[str] = None
    data: Optional[Dict] = None
    template_id: Optional[str] = None

class AIGenerateRequest(BaseModel):
    job_title: str
    experience_level: str
    industry: str
    current_summary: Optional[str] = ""

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_jwt_token(user_id: int, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    return payload

# AI-powered content generation
def generate_cv_content(job_title: str, experience_level: str, industry: str, current_summary: str = "") -> Dict:
    """Generate AI-powered CV content suggestions"""

    # Rule-based suggestions (fallback if AI model fails)
    suggestions = {
        "software engineer": [
            "Developed and maintained scalable web applications using modern frameworks",
            "Implemented automated testing pipelines reducing deployment time by 40%",
            "Led cross-functional teams to deliver high-quality software solutions",
            "Optimized database queries improving application performance by 60%"
        ],
        "marketing manager": [
            "Increased brand awareness by 150% through integrated digital campaigns",
            "Managed multi-channel marketing budget exceeding $500,000 annually",
            "Launched successful product campaigns generating $2M+ in revenue",
            "Built and mentored high-performing marketing team of 8 professionals"
        ],
        "data scientist": [
            "Built machine learning models achieving 95%+ accuracy in predictions",
            "Analyzed complex datasets to drive strategic business decisions",
            "Implemented predictive analytics solutions saving $1M annually",
            "Presented data insights to C-level executives and stakeholders"
        ],
        "product manager": [
            "Successfully launched 5 product features increasing user engagement by 35%",
            "Managed product roadmap and coordinated with engineering teams",
            "Conducted user research and A/B testing to optimize product features",
            "Drove product strategy resulting in 25% increase in customer retention"
        ]
    }

    job_key = job_title.lower()
    default_suggestions = [
        "Demonstrated strong leadership and problem-solving abilities",
        "Achieved significant results in previous professional roles",
        "Collaborated effectively with cross-functional teams",
        "Continuously improved processes and operational efficiency"
    ]

    # Try AI generation first
    if cv_generator:
        try:
            prompt = f"Professional achievement for {job_title} with {experience_level} experience:"
            ai_response = cv_generator(prompt, max_length=50, num_return_sequences=1)
            ai_text = ai_response[0]['generated_text'].replace(prompt, "").strip()
            if ai_text and len(ai_text) > 10:
                return {
                    "suggestions": [ai_text] + suggestions.get(job_key, default_suggestions)[:3],
                    "generated_summary": f"Results-driven {job_title} with {experience_level} experience in {industry}. {ai_text}"
                }
        except Exception as e:
            print(f"AI generation failed: {e}")

    # Fallback to rule-based
    job_suggestions = suggestions.get(job_key, default_suggestions)
    return {
        "suggestions": job_suggestions[:4],
        "generated_summary": f"Experienced {job_title} with proven track record in {industry}. Skilled in delivering high-quality results and driving business growth."
    }

# API Routes

@app.get("/")
async def root():
    return {"message": "AI CV Builder API is running!"}

@app.post("/auth/register")
async def register_user(user: UserCreate):
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash, full_name) VALUES (?, ?, ?)",
            (user.email, hash_password(user.password), user.full_name)
        )
        conn.commit()
        user_id = cursor.lastrowid

        token = create_jwt_token(user_id, user.email)
        return {"message": "User registered successfully", "token": token, "user_id": user_id}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()

@app.post("/auth/login")
async def login_user(user: UserLogin):
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user or not verify_password(user.password, db_user[1]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token(db_user[0], user.email)
    return {"message": "Login successful", "token": token, "user_id": db_user[0]}

@app.post("/ai/generate")
async def generate_ai_content(request: AIGenerateRequest, current_user: dict = Depends(get_current_user)):
    """Generate AI-powered CV content"""
    try:
        content = generate_cv_content(
            request.job_title,
            request.experience_level,
            request.industry,
            request.current_summary
        )
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@app.post("/cvs")
async def create_cv(cv: CVCreate, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    cv_data = {
        "full_name": cv.full_name,
        "email": cv.email,
        "phone": cv.phone,
        "job_title": cv.job_title,
        "summary": cv.summary,
        "experience": cv.experience,
        "education": cv.education,
        "skills": cv.skills,
        "languages": cv.languages,
        "certifications": cv.certifications
    }

    cursor.execute(
        "INSERT INTO cvs (user_id, title, data, template_id) VALUES (?, ?, ?, ?)",
        (current_user["user_id"], cv.title, json.dumps(cv_data), cv.template_id)
    )
    conn.commit()
    cv_id = cursor.lastrowid
    conn.close()

    return {"message": "CV created successfully", "cv_id": cv_id}

@app.get("/cvs")
async def get_user_cvs(current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, template_id, created_at FROM cvs WHERE user_id = ?",
        (current_user["user_id"],)
    )
    cvs = cursor.fetchall()
    conn.close()

    return [
        {
            "id": cv[0],
            "title": cv[1],
            "template_id": cv[2],
            "created_at": cv[3]
        }
        for cv in cvs
    ]

@app.get("/cvs/{cv_id}")
async def get_cv(cv_id: int, current_user: dict = Depends(get_current_user)):
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT title, data, template_id FROM cvs WHERE id = ? AND user_id = ?",
        (cv_id, current_user["user_id"])
    )
    cv = cursor.fetchone()
    conn.close()

    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")

    return {
        "title": cv[0],
        "data": json.loads(cv[1]),
        "template_id": cv[2]
    }

@app.get("/templates")
async def get_templates():
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, category, is_premium FROM templates")
    templates = cursor.fetchall()
    conn.close()

    return [
        {
            "id": template[0],
            "name": template[1],
            "category": template[2],
            "is_premium": bool(template[3])
        }
        for template in templates
    ]

@app.get("/templates/{template_id}")
async def get_template(template_id: str):
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, html_content, css_styles FROM templates WHERE id = ?",
        (template_id,)
    )
    template = cursor.fetchone()
    conn.close()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "name": template[0],
        "html_content": template[1],
        "css_styles": template[2]
    }

@app.post("/cvs/{cv_id}/export/pdf")
async def export_cv_pdf(cv_id: int, current_user: dict = Depends(get_current_user)):
    # Get CV data
    conn = sqlite3.connect('cv_builder.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT data FROM cvs WHERE id = ? AND user_id = ?",
        (cv_id, current_user["user_id"])
    )
    cv_data = cursor.fetchone()
    conn.close()

    if not cv_data:
        raise HTTPException(status_code=404, detail="CV not found")

    data = json.loads(cv_data[0])

    # Generate PDF
    filename = f"cv_{cv_id}_{uuid.uuid4().hex[:8]}.pdf"
    
    # Create temp directory
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, filename)

    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Add content
    story.append(Paragraph(data.get('full_name', 'Your Name'), styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(data.get('job_title', 'Your Job Title'), styles['Heading2']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Email: {data.get('email', '')}", styles['Normal']))
    story.append(Paragraph(f"Phone: {data.get('phone', '')}", styles['Normal']))
    story.append(Spacer(1, 12))

    if data.get('summary'):
        story.append(Paragraph("Professional Summary", styles['Heading2']))
        story.append(Paragraph(data['summary'], styles['Normal']))
        story.append(Spacer(1, 12))

    if data.get('experience'):
        story.append(Paragraph("Experience", styles['Heading2']))
        story.append(Paragraph(data['experience'], styles['Normal']))
        story.append(Spacer(1, 12))

    if data.get('education'):
        story.append(Paragraph("Education", styles['Heading2']))
        story.append(Paragraph(data['education'], styles['Normal']))
        story.append(Spacer(1, 12))

    if data.get('skills'):
        story.append(Paragraph("Skills", styles['Heading2']))
        skills_text = ', '.join(data['skills']) if isinstance(data['skills'], list) else data['skills']
        story.append(Paragraph(skills_text, styles['Normal']))

    try:
        doc.build(story)
        return FileResponse(filepath, media_type='application/pdf', filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)