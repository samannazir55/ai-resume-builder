import sys
import os
sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models.template import Template

def clean_startup_template():
    db = SessionLocal()
    print("🎨 Refining Startup Template...")
    
    clean_css = """
    :root { --primary: {{accent_color}}; --font: {{font_family}}; }
    .resume-start { 
        display: flex; 
        font-family: var(--font), sans-serif; 
        min-height: 1000px; 
        height: auto;
        background: #fff;
        position: relative;
    }
    
    /* Left Sidebar */
    .start-sidebar { 
        width: 30%; 
        min-width: 250px;
        background: #111; 
        color: white; 
        padding: 40px 20px; 
        display: flex; 
        flex-direction: column;
        flex-shrink: 0;
    }
    
    /* Content Area */
    .start-body { 
        width: 70%; 
        padding: 40px; 
        position: relative;
    }
    
    h1 { font-size: 32px; margin: 0 0 10px 0; line-height: 1.1; }
    h3 { font-size: 16px; font-weight: 300; opacity: 0.8; margin-bottom: 40px; color: var(--primary); text-transform: uppercase; letter-spacing: 1px; }
    
    .start-img-container img { 
        width: 120px; height: 120px; 
        border-radius: 50%; 
        border: 4px solid var(--primary);
        object-fit: cover; 
        margin-bottom: 30px; 
    }
    
    .start-label { font-size: 11px; text-transform: uppercase; color: #888; margin-bottom: 5px; letter-spacing: 1px; border-bottom: 1px solid #333; display: inline-block; padding-bottom: 2px; }
    .tag { display: inline-block; background: #333; padding: 4px 8px; font-size: 11px; border-radius: 4px; margin: 2px; }
    
    /* Headers with Shadow Effect */
    .shadow-head { 
        font-size: 24px; 
        color: #333; 
        margin: 0 0 20px 0; 
        position: relative; 
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: -1px;
    }
    
    .content { margin-bottom: 40px; line-height: 1.6; font-size: 14px; color: #444; }
    .content p, .content li { margin-bottom: 8px; }
    """
    
    # 1. Update Template
    t = db.query(Template).filter(Template.id == "startup_bold").first()
    if t:
        t.css_styles = clean_css
        db.commit()
        print("✅ FIXED: Startup Bold CSS cleaned up (Fixed spacing & overlays).")
    else:
        print("⚠️ Warning: Startup Bold template not found (maybe run injection script first).")
    
    db.close()

if __name__ == "__main__":
    clean_startup_template()