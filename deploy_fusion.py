import os

# We overwrite the PDF generation service.
# Goal: 100% prevent double hashtags.

path = os.path.join("backend", "app", "services", "file_service.py")

new_file_service = """
import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

# --- HELPER: SAFE COLOR GENERATOR ---
def ensure_single_hash(color_value, default_hex="#333333"):
    if not color_value: 
        return default_hex
        
    s = str(color_value).strip().replace('"', '').replace("'", "")
    
    # If it's already a var, ignore it
    if s.startswith("var("): return default_hex
    
    # Remove ALL hashes first
    clean = s.replace("#", "")
    
    # Valid hex check (3 or 6 chars)
    if len(clean) not in [3, 6]:
        return default_hex
        
    # Return with EXACTLY one hash
    return f"#{clean}"

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    # 1. PREPARE VARIABLES
    # React usually sends 'accentColor', 'textColor'. 
    # AI or older code sends 'accent_color'.
    
    accent = ensure_single_hash(cv_data.get('accentColor') or cv_data.get('accent_color'), "#2c3e50")
    text_col = ensure_single_hash(cv_data.get('textColor') or cv_data.get('text_color'), "#333333")
    
    font_name = cv_data.get('fontFamily') or cv_data.get('font_family') or "sans-serif"
    # sanitize font string
    font_name = font_name.replace(";", "").replace('"', '').replace("'", "")

    # 2. DATA CLEANING FOR TEMPLATE (Pystache)
    render_data = {
        **cv_data,
        "accent_color": accent,
        "text_color": text_col,
        "font_family": font_name,
        # Helper for HTML line breaks
        "experience": (cv_data.get('experience') or '').replace('\\n', '<br/>'),
        "education": (cv_data.get('education') or '').replace('\\n', '<br/>')
    }

    # 3. COMPILE CSS VARIABLES (Hard Substitution)
    # This removes the need for Weasyprint to resolve var() which often fails on syntax
    
    compiled_css = template_css
    
    # Explicit mapping
    var_map = {
        "var(--primary)": accent,
        "var(--text-color)": text_col,
        "var(--text)": text_col,
        "var(--font)": font_name,
        "{{accent_color}}": accent,  # catch handlebars
        "#{{accent_color}}": accent, # catch accidental hash before handlebar
    }
    
    for key, val in var_map.items():
        # Case insensitive replacement for safety could be better but str.replace is faster
        compiled_css = compiled_css.replace(key, val)

    # 4. FINAL REGEX CLEANUP (The Safety Net)
    # Fix any '##' created by edge cases
    compiled_css = re.sub(r'#+#', '#', compiled_css)
    # Fix 'color: ;' or 'color: #;'
    compiled_css = re.sub(r':\s*#?;', f':{text_col};', compiled_css)

    # 5. RENDER CONTENT
    compiled_html = pystache.render(template_html, render_data)

    # 6. GENERATE PDF
    try:
        # We append a Force Override header to ensure user preferences beat template defaults
        overrides = f\"\"\"
        body, p, li, span, div {{ color: {text_col} !important; font-family: {font_name} !important; }}
        h1, h2, h3, h4, h5, .header, .title {{ color: {accent} !important; }}
        \"\"\"
        final_css_string = overrides + "\\n" + compiled_css
        
        doc = HTML(string=compiled_html)
        style = CSS(string=final_css_string)
        
        return doc.write_pdf(stylesheets=[style], presentational_hints=True)
        
    except Exception as e:
        print(f"PDF ENGINE ERROR: {e}")
        # Create a Debug PDF so user knows what happened instead of 500 error
        err_msg = f"<h1>PDF Gen Failed</h1><p>{str(e)}</p>"
        return HTML(string=err_msg).write_pdf()

def create_docx_from_data(cv_data: dict) -> bytes:
    # DOCX Generator (Standard)
    document = docx.Document()
    document.add_heading(cv_data.get('fullName', 'Candidate'), 0)
    document.add_paragraph(f"{cv_data.get('email','')} | {cv_data.get('phone','')}")
    
    sections = ['summary', 'experience', 'education', 'skills']
    for sec in sections:
        val = cv_data.get(sec, "")
        if val:
            document.add_heading(sec.capitalize(), 1)
            # Basic HTML stripping
            clean = str(val).replace("<br/>", "\\n").replace("<ul>","").replace("</ul>","").replace("<li>", "• ").replace("</li>", "\\n")
            for line in clean.split('\\n'):
                if line.strip(): document.add_paragraph(line.strip())

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()
"""

try:
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_file_service)
    print("✅ FILE SERVICE OVERWRITTEN.")
    print("   - Includes `ensure_single_hash` helper.")
    print("   - Logic checks for existing # before adding one.")
except Exception as e:
    print(f"❌ Error: {e}")