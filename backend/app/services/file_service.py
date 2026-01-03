import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    # 1. Clean Variables
    clean_vars = {**cv_data}
    
    # Strip existing hash if present in variable
    for key in ['accentColor', 'textColor']:
        val = clean_vars.get(key)
        if val and isinstance(val, str) and val.startswith('#'):
            clean_vars[key] = val  # keep full hex for direct use
            # Also provide a 'raw' version without hash if template prepends it
            # But safer -> Template should use variable direct.
            
    # Normalize keys for template
    clean_vars['accent_color'] = clean_vars.get('accentColor', '#2c3e50')
    clean_vars['text_color'] = clean_vars.get('textColor', '#333333')
    clean_vars['font_family'] = clean_vars.get('fontFamily', 'sans-serif')

    # 2. Render CSS
    rendered_css = pystache.render(template_css, clean_vars)
    
    # 3. ANTI-DOUBLE HASH REGEX
    # Fixes 'color: ##FF0000' -> 'color: #FF0000'
    rendered_css = re.sub(r'#+#', '#', rendered_css)

    rendered_html = pystache.render(template_html, clean_vars)

    html = HTML(string=rendered_html)
    css = CSS(string=rendered_css)
    
    return html.write_pdf(stylesheets=[css])

def create_docx_from_data(cv_data: dict) -> bytes:
    document = docx.Document()
    document.add_heading(cv_data.get('fullName', 'Name'), 0)
    document.add_paragraph(f"{cv_data.get('email')} | {cv_data.get('phone')}")
    
    for sec in ['summary', 'experience', 'education']:
        if cv_data.get(sec):
            document.add_heading(sec.capitalize(), 1)
            # Remove HTML tags for Docx
            clean_text = cv_data.get(sec, "").replace("<br/>", "\n").replace("<ul>","").replace("</ul>","").replace("<li>","• ").replace("</li>","")
            document.add_paragraph(clean_text)
            
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()
