import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

def sanitize_color(val):
    """Ensures color has exactly one # prefix and is valid hex"""
    if not val: 
        return "333333"  # NO HASH - template will add it
    
    # Remove ALL hashes
    clean = str(val).replace("#", "").strip()
    
    # Validate hex format
    if not re.match(r'^[0-9A-Fa-f]{3,6}$', clean):
        return "333333"  # Fallback, NO HASH
    
    return clean  # Return WITHOUT hash

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    """Generate PDF from template - CRITICAL FIX for # issue"""
    
    # 1. Prepare data WITHOUT hashes in colors
    render_data = {
        "full_name": cv_data.get("fullName") or cv_data.get("full_name") or "Name",
        "job_title": cv_data.get("jobTitle") or cv_data.get("job_title") or "Job Title",
        "email": cv_data.get("email") or "",
        "phone": cv_data.get("phone") or "",
        "location": cv_data.get("location") or "",
        "summary": cv_data.get("summary") or "",
        "experience": cv_data.get("experience") or "",
        "education": cv_data.get("education") or "",
        "skills": cv_data.get("skills") if isinstance(cv_data.get("skills"), list) else [],
        
        # CRITICAL: Colors WITHOUT hash
        "accent_color": sanitize_color(cv_data.get("accent_color") or cv_data.get("accentColor") or "#2c3e50"),
        "text_color": sanitize_color(cv_data.get("text_color") or cv_data.get("textColor") or "#333333"),
        "font_family": cv_data.get("fontFamily") or cv_data.get("font_family") or "Arial, sans-serif",
    }
    
    try:
        # 2. First, replace ALL {{color}} with #{{color}} in CSS template
        # This ensures colors ALWAYS have exactly one hash
        css_fixed = re.sub(r':\s*\{\{(accent_color|text_color)\}\}', r': #\{\{\1\}\}', template_css)
        
        # 3. Now render with Mustache (colors don't have # in data)
        rendered_html = pystache.render(template_html, render_data)
        rendered_css = pystache.render(css_fixed, render_data)
        
        # 4. Final safety check - remove any double/triple hashes
        rendered_css = re.sub(r'#{2,}', '#', rendered_css)
        
        # 5. Remove any unrendered Mustache tags
        rendered_css = re.sub(r'\{\{[^}]+\}\}', '', rendered_css)
        
        # 6. Debug output
        print("=" * 60)
        print("🎨 RENDER DATA:")
        print(f"  accent_color: {render_data['accent_color']}")
        print(f"  text_color: {render_data['text_color']}")
        print("\n📄 CSS (first 400 chars):")
        print(rendered_css[:400])
        print("=" * 60)
        
        # 7. Generate PDF
        html_obj = HTML(string=rendered_html)
        css_obj = CSS(string=rendered_css)
        
        pdf_bytes = html_obj.write_pdf(stylesheets=[css_obj], presentational_hints=True)
        
        print("✅ PDF generated successfully!")
        return pdf_bytes
        
    except Exception as e:
        print(f"❌ PDF ERROR: {e}")
        print(f"\n🔍 CSS around error position:")
        if 'at' in str(e):
            # Extract position number from error message
            match = re.search(r'at (\d+)', str(e))
            if match:
                pos = int(match.group(1))
                start = max(0, pos - 50)
                end = min(len(rendered_css), pos + 50)
                print(f"Position {pos}: ...{rendered_css[start:end]}...")
                print(f"Character at {pos}: '{rendered_css[pos] if pos < len(rendered_css) else 'N/A'}'")
        
        raise Exception(f"PDF generation failed: {str(e)}")

def create_docx_from_data(cv_data: dict) -> bytes:
    """Generate DOCX from CV data"""
    document = docx.Document()
    
    # Header
    document.add_heading(cv_data.get('fullName') or cv_data.get('full_name', 'Name'), 0)
    contact = f"{cv_data.get('email', '')} | {cv_data.get('phone', '')}"
    document.add_paragraph(contact)
    
    # Sections
    sections = [
        ('summary', 'Summary'),
        ('professional_summary', 'Professional Summary'),
        ('experience', 'Experience'),
        ('education', 'Education')
    ]
    
    for key, title in sections:
        text = cv_data.get(key, "")
        if text:
            document.add_heading(title, 1)
            
            if isinstance(text, list):
                for item in text:
                    document.add_paragraph(str(item), style='List Bullet')
            else:
                # Clean HTML
                clean_text = re.sub(r'<[^>]+>', '', str(text))
                clean_text = clean_text.replace('&nbsp;', ' ').strip()
                
                if clean_text:
                    # Split by bullets
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