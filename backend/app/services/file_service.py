import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

def ensure_single_hash(color_value, default_hex="333333"):
    """Returns ONLY the hex digits (no hash)"""
    if not color_value: 
        return default_hex
        
    s = str(color_value).strip().replace('"', '').replace("'", "")
    
    if s.startswith("var("): 
        return default_hex
    
    # Remove ALL hashes
    clean = s.replace("#", "")
    
    # Validate hex
    if not re.match(r'^[0-9a-fA-F]{3}$|^[0-9a-fA-F]{6}$', clean):
        return default_hex
        
    return clean  # Return WITHOUT hash

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    # Get colors WITHOUT hash (templates will add it)
    accent = ensure_single_hash(cv_data.get('accentColor') or cv_data.get('accent_color'), "2c3e50")
    text_col = ensure_single_hash(cv_data.get('textColor') or cv_data.get('text_color'), "333333")
    
    font_name = cv_data.get('fontFamily') or cv_data.get('font_family') or "sans-serif"
    font_name = re.sub(r'[;"\']+', '', font_name)

    # Prepare data for Mustache
    render_data = {
        **cv_data,
        "accent_color": accent,  # No hash - template adds it
        "text_color": text_col,   # No hash - template adds it
        "font_family": font_name,
        "experience": (cv_data.get('experience') or '').replace('\n', '<br/>'),
        "education": (cv_data.get('education') or '').replace('\n', '<br/>')
    }

    # Render HTML and CSS
    compiled_html = pystache.render(template_html, render_data)
    compiled_css = pystache.render(template_css, render_data)

    # Safety cleanup
    compiled_css = re.sub(r'##+', '#', compiled_css)  # Fix double hashes
    compiled_css = re.sub(r':\s*#?\s*;', f': #{text_col};', compiled_css)  # Fix empty values

    # Generate PDF
    try:
        doc = HTML(string=compiled_html)
        style = CSS(string=compiled_css)
        return doc.write_pdf(stylesheets=[style], presentational_hints=True)
        
    except Exception as e:
        print(f"PDF ERROR: {e}")
        print(f"CSS Preview:\n{compiled_css[:500]}")
        
        # Return error PDF
        err_msg = f"<h1>PDF Failed</h1><p>{str(e)}</p>"
        return HTML(string=err_msg).write_pdf()

def create_docx_from_data(cv_data: dict) -> bytes:
    document = docx.Document()
    document.add_heading(cv_data.get('fullName', 'Candidate'), 0)
    document.add_paragraph(f"{cv_data.get('email','')} | {cv_data.get('phone','')}")
    
    sections = ['summary', 'experience', 'education', 'skills']
    for sec in sections:
        val = cv_data.get(sec, "")
        if val:
            document.add_heading(sec.capitalize(), 1)
            clean = str(val).replace("<br/>", "\n").replace("<ul>","").replace("</ul>","")
            clean = clean.replace("<li>", "• ").replace("</li>", "\n")
            for line in clean.split('\n'):
                if line.strip(): 
                    document.add_paragraph(line.strip())

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()