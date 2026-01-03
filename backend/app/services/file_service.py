import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

# HELPER: Color Normalizer
def sanitize_color(val):
    """Ensures color has exactly one # prefix"""
    if not val: 
        return "#333333"
    clean = str(val).replace("#", "").strip()
    # Validate hex format
    if not re.match(r'^[0-9A-Fa-f]{3,6}$', clean):
        return "#333333"  # Fallback to default
    return f"#{clean}"

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    """Generate PDF from template with proper error handling"""
    
    # 1. Prepare Safe Data
    render_data = {
        **cv_data,
        "accent_color": sanitize_color(cv_data.get("accent_color") or cv_data.get("accentColor") or "#2c3e50"),
        "text_color": sanitize_color(cv_data.get("text_color") or cv_data.get("textColor") or "#333333"),
        "font_family": cv_data.get("fontFamily") or cv_data.get("font_family") or "Arial, sans-serif",
        
        # Ensure basic fields exist
        "full_name": cv_data.get("fullName") or cv_data.get("full_name") or "Name",
        "job_title": cv_data.get("jobTitle") or cv_data.get("job_title") or "Job Title",
        "email": cv_data.get("email") or "",
        "phone": cv_data.get("phone") or "",
        "summary": cv_data.get("summary") or "",
        "experience": cv_data.get("experience") or "",
        "education": cv_data.get("education") or "",
        
        # Handle skills array
        "skills": cv_data.get("skills") if isinstance(cv_data.get("skills"), list) else []
    }

    try:
        # 2. Render HTML first (this handles {{#skills}} loops)
        rendered_html = pystache.render(template_html, render_data)
        
        # 3. Render CSS separately (NO loops here, only variables)
        rendered_css = pystache.render(template_css, render_data)
        
        # 4. Post-process CSS to fix any double-hash issues
        rendered_css = re.sub(r'#{2,}', '#', rendered_css)  # Replace ## or more with single #
        
        # 5. Validate CSS doesn't contain Mustache syntax
        if '{{' in rendered_css or '}}' in rendered_css:
            print("⚠️ WARNING: Unrendered Mustache tags in CSS:", rendered_css[:200])
            # Remove any remaining Mustache tags
            rendered_css = re.sub(r'\{\{[^}]+\}\}', '', rendered_css)
        
        # 6. Debug log
        print("✅ CSS first 200 chars:", rendered_css[:200])
        print("✅ HTML first 200 chars:", rendered_html[:200])
        
        # 7. Generate PDF
        html_obj = HTML(string=rendered_html)
        css_obj = CSS(string=rendered_css)
        
        pdf_bytes = html_obj.write_pdf(stylesheets=[css_obj], presentational_hints=True)
        
        print("✅ PDF generated successfully")
        return pdf_bytes
        
    except Exception as e:
        print(f"❌ PDF Generation Error: {e}")
        print(f"CSS content: {rendered_css[:500]}")
        print(f"HTML content: {rendered_html[:500]}")
        raise Exception(f"PDF generation failed: {str(e)}")

def create_docx_from_data(cv_data: dict) -> bytes:
    """Generate DOCX from CV data"""
    document = docx.Document()
    
    # Header
    document.add_heading(cv_data.get('fullName') or cv_data.get('full_name', 'Name'), 0)
    contact = f"{cv_data.get('email', '')} | {cv_data.get('phone', '')}"
    document.add_paragraph(contact)
    
    # Sections
    for section in ['summary', 'professional_summary', 'experience', 'education']:
        text = cv_data.get(section, "")
        if text:
            document.add_heading(section.replace('_', ' ').title(), 1)
            
            if isinstance(text, list):
                for item in text:
                    document.add_paragraph(str(item), style='List Bullet')
            else:
                # Clean HTML
                clean_text = re.sub(r'<[^>]+>', '', str(text))  # Strip HTML tags
                clean_text = clean_text.replace('\n', ' ').strip()
                
                if clean_text:
                    # Split into bullet points if contains bullets
                    if '•' in clean_text:
                        bullets = [b.strip() for b in clean_text.split('•') if b.strip()]
                        for bullet in bullets:
                            document.add_paragraph(bullet, style='List Bullet')
                    else:
                        document.add_paragraph(clean_text)
    
    # Skills
    skills = cv_data.get('skills', [])
    if skills:
        document.add_heading('Skills', 1)
        if isinstance(skills, list):
            document.add_paragraph(', '.join(skills))
        else:
            document.add_paragraph(str(skills))
    
    # Save to bytes
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()