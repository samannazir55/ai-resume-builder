import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

def ensure_single_hash(color_value, default_hex="#333333"):
    if not color_value: 
        return default_hex
        
    s = str(color_value).strip().replace('"', '').replace("'", "")
    
    if s.startswith("var("): 
        return default_hex
    
    # Remove ALL hashes first
    clean = s.replace("#", "")
    
    # Valid hex check (3 or 6 chars)
    if not re.match(r'^[0-9a-fA-F]{3}$|^[0-9a-fA-F]{6}$', clean):
        return default_hex
        
    return f"#{clean}"

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    # 1. PREPARE VARIABLES (NO HASH PREFIX)
    accent = ensure_single_hash(cv_data.get('accentColor') or cv_data.get('accent_color'), "#2c3e50")
    text_col = ensure_single_hash(cv_data.get('textColor') or cv_data.get('text_color'), "#333333")
    
    # CRITICAL: Store WITHOUT hash for Mustache templates
    accent_no_hash = accent.lstrip('#')
    text_no_hash = text_col.lstrip('#')
    
    font_name = cv_data.get('fontFamily') or cv_data.get('font_family') or "sans-serif"
    font_name = re.sub(r'[;"\']+', '', font_name)

    # 2. DATA CLEANING FOR TEMPLATE
    render_data = {
        **cv_data,
        # Provide BOTH versions
        "accent_color": accent_no_hash,  # For Mustache: #{{accent_color}}
        "accent_color_full": accent,      # For var substitution
        "text_color": text_no_hash,
        "text_color_full": text_col,
        "font_family": font_name,
        "experience": (cv_data.get('experience') or '').replace('\n', '<br/>'),
        "education": (cv_data.get('education') or '').replace('\n', '<br/>')
    }

    # 3. RENDER TEMPLATE FIRST
    compiled_html = pystache.render(template_html, render_data)

    # 4. FIX ANY DOUBLE HASHES IN HTML (before CSS processing)
    compiled_html = re.sub(r'##+', '#', compiled_html)

    # 5. COMPILE CSS VARIABLES
    compiled_css = template_css
    
    var_map = {
        "var(--primary)": accent,
        "var(--text-color)": text_col,
        "var(--text)": text_col,
        "var(--font)": font_name,
        "{{accent_color}}": accent_no_hash,  # No hash for Mustache
        "{{text_color}}": text_no_hash,
    }
    
    for key, val in var_map.items():
        compiled_css = compiled_css.replace(key, val)

    # 6. AGGRESSIVE CLEANUP
    # Fix any double hashes
    compiled_css = re.sub(r'##+', '#', compiled_css)
    # Fix empty color values
    compiled_css = re.sub(r':\s*#?\s*;', f': {text_col};', compiled_css)
    # Fix malformed hex (non-hex chars after #)
    compiled_css = re.sub(r'#[^0-9a-fA-F\s;}{]', f'#{text_no_hash}', compiled_css)

    # 7. GENERATE PDF with better error handling
    try:
        overrides = f"""
        body, p, li, span, div {{ color: {text_col} !important; font-family: {font_name}, sans-serif !important; }}
        h1, h2, h3, h4, h5, .header, .title {{ color: {accent} !important; }}
        """
        final_css_string = overrides + "\n" + compiled_css
        
        # Debug: Print first 500 chars to log
        print("CSS Preview:", final_css_string[:500])
        
        doc = HTML(string=compiled_html)
        style = CSS(string=final_css_string)
        
        return doc.write_pdf(stylesheets=[style], presentational_hints=True)
        
    except Exception as e:
        print(f"PDF ENGINE ERROR: {e}")
        print(f"CSS causing error:\n{final_css_string}")
        
        # Fallback with minimal CSS
        try:
            doc = HTML(string=compiled_html)
            return doc.write_pdf()
        except:
            err_msg = f"<h1>PDF Generation Failed</h1><p>{str(e)}</p><pre>{compiled_css[:200]}</pre>"
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