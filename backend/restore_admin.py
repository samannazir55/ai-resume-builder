import sys
import os

# Ensure we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import template as models

def init_db():
    print("⏳ Connecting to database...")
    
    # 1. CREATE TABLES (Fixes 'no such table' error)
    # This checks all models and creates missing tables in sql_app.db
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables checked/created.")

    db = SessionLocal()
    
    try:
        print("🛠️  Updating Templates...")
        
        # DEFINITION: Corrected Modern Template
        modern_data = {
            "id": "modern",
            "name": "Modern Creative",
            "category": "creative",
            "is_premium": True,
            "html_content": """
            <div class="cv-modern-wrapper">
                <aside class="cv-sidebar">
                    <div class="profile-container">
                        <div class="avatar-box">
                            <span>{{full_name_initials}}</span>
                        </div>
                    </div>
                    
                    <div class="sidebar-text-content">
                        <h1 class="sidebar-name">{{full_name}}</h1>
                        <p class="sidebar-job">{{job_title}}</p>
                        
                        <div class="sidebar-info">
                            <div class="info-item">{{email}}</div>
                            <div class="info-item">{{phone}}</div>
                            <div class="info-item">{{location}}</div>
                        </div>

                        <div class="skills-section">
                            <h3>Skills</h3>
                            <div class="skill-tags">
                                {{#skills}}
                                <span class="tag">{{.}}</span>
                                {{/skills}}
                            </div>
                        </div>
                    </div>
                </aside>

                <main class="cv-main-content">
                    <section class="main-section">
                        <h2 class="section-title">Professional Summary</h2>
                        <div class="content-text">
                            {{{summary}}}
                        </div>
                    </section>

                    <section class="main-section">
                        <h2 class="section-title">Experience</h2>
                        <div class="experience-list">
                            {{{experience}}}
                        </div>
                    </section>

                    <section class="main-section">
                        <h2 class="section-title">Education</h2>
                        <div class="education-list">
                            {{{education}}}
                        </div>
                    </section>
                </main>
            </div>
            """,
            "css_styles": """
            /* SCOPED ROOT */
            .cv-modern-wrapper { 
                font-family: {{font_family}}, sans-serif; 
                display: flex;
                width: 100%;
                min-height: 100vh;
                background: white;
                overflow: hidden;
            }

            /* LEFT SIDEBAR - Forced White Text */
            .cv-modern-wrapper .cv-sidebar {
                width: 35%;
                background-color: {{accent_color}}; 
                color: #ffffff !important;
                padding: 40px 20px;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
            }

            .cv-modern-wrapper .sidebar-name {
                color: #ffffff !important;
                font-size: 2em;
                margin-top: 20px;
                line-height: 1.2;
            }
            
            .cv-modern-wrapper .sidebar-job {
                color: rgba(255, 255, 255, 0.9) !important;
                font-size: 1.1em;
                margin-bottom: 30px;
                font-weight: 300;
            }

            .cv-modern-wrapper .info-item {
                color: rgba(255, 255, 255, 0.95) !important;
                margin-bottom: 10px;
            }

            .cv-modern-wrapper .skills-section h3 {
                color: #ffffff !important;
                border-bottom: 1px solid rgba(255,255,255,0.3);
                margin: 30px 0 15px 0;
            }

            .cv-modern-wrapper .tag {
                background: rgba(255,255,255,0.2);
                color: #ffffff !important;
                padding: 5px 10px;
                border-radius: 4px;
                display: inline-block;
                margin: 3px;
                font-size: 0.85em;
            }

            .cv-modern-wrapper .avatar-box {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                background: rgba(255,255,255,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.5em;
                color: white !important;
                border: 2px solid white;
            }

            /* RIGHT CONTENT - Dynamic Text Color */
            .cv-modern-wrapper .cv-main-content {
                flex: 1;
                padding: 40px;
                background: white;
                color: {{text_color}}; 
            }

            .cv-modern-wrapper .section-title {
                color: {{accent_color}};
                border-bottom: 2px solid #eee;
                padding-bottom: 8px;
                margin-bottom: 15px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            .cv-modern-wrapper .content-text,
            .cv-modern-wrapper .experience-list,
            .cv-modern-wrapper .education-list {
                color: {{text_color}};
                line-height: 1.6;
            }
            """
        }

        # 3. UPSERT (Update if exists, Insert if new)
        existing = db.query(models.Template).filter(models.Template.id == modern_data['id']).first()
        
        if existing:
            print(f"🔄 Updating '{modern_data['name']}'...")
            existing.html_content = modern_data['html_content']
            existing.css_styles = modern_data['css_styles']
            existing.name = modern_data['name']
        else:
            print(f"✨ Creating '{modern_data['name']}'...")
            t = models.Template(**modern_data)
            db.add(t)

        db.commit()
        print("✅ SUCCESS: Modern Template restored correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()