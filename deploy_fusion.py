import os

# We are overwriting the PDF Generator Service to add a "Sanitizer" step.
file_service_path = os.path.join("backend", "app", "services", "file_service.py")

sanitizer_code = """import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

# HELPER: Color Normalizer
# Ensures every color has exactly one '#' prefix
def sanitize_color(val):
    if not val: return "#333333"
    # Remove all hashes first
    clean = str(val).replace("#", "").strip()
    # Add exactly one hash back
    return f"#{clean}"

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    # 1. Prepare Safe Data Variables
    render_data = {
        **cv_data,
        # Force sanitize colors to avoid ##HEX issues
        "accent_color": sanitize_color(cv_data.get("accent_color") or cv_data.get("accentColor") or "#2c3e50"),
        "text_color": sanitize_color(cv_data.get("text_color") or cv_data.get("textColor") or "#333333"),
        "font_family": cv_data.get("fontFamily") or cv_data.get("font_family") or "sans-serif"
    }

    # 2. Render Template Strings
    # Note: If the template itself has a hardcoded hash like "color: #{{val}}", 
    # and our val has "#", we get double. We will fix this in post-processing.
    rendered_html = pystache.render(template_html, render_data)
    rendered_css = pystache.render(template_css, render_data)

    # 3. CRITICAL POST-PROCESSING FIX
    # We use Regex to turn '##', '###', '####' into a single '#'
    # This prevents the 'Unexpected char #' error in WeasyPrint
    rendered_css = re.sub(r'#+', '#', rendered_css)

    # 4. Generate PDF
    # We use presentational_hints=True to support HTML attributes like 'align'
    html = HTML(string=rendered_html)
    css = CSS(string=rendered_css)
    
    return html.write_pdf(stylesheets=[css], presentational_hints=True)

def create_docx_from_data(cv_data: dict) -> bytes:
    document = docx.Document()
    
    document.add_heading(cv_data.get('fullName') or cv_data.get('full_name', 'Name'), 0)
    contact = f"{cv_data.get('email', '')} | {cv_data.get('phone', '')}"
    document.add_paragraph(contact)
    
    for section in ['summary', 'professional_summary', 'experience', 'education']:
        text = cv_data.get(section, "")
        if text:
            # Title case header (e.g. "Experience")
            document.add_heading(section.replace('_', ' ').capitalize(), 1)
            
            # Simple text cleaning
            if isinstance(text, list):
                # If bullet points array
                for item in text:
                    document.add_paragraph(item, style='List Bullet')
            else:
                # If HTML string
                clean_text = text.replace("<br>", "\\n").replace("<br/>", "\\n").replace("<ul>","").replace("</ul>","").replace("<li>", "").replace("</li>", "\\n")
                lines = clean_text.split('\\n')
                for line in lines:
                    if line.strip():
                        # Basic heuristics: start with bullet if short
                        document.add_paragraph(line.strip())

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()
"""

try:
    with open(file_service_path, "w", encoding="utf-8") as f:
        f.write(sanitizer_code)
    print("✅ FILE SERVICE PATCHED.")
    print("   - CSS 'Color Sanitizer' installed.")
    print("   - This will fix 'Unexpected char #' errors permanently.")
    print("   - PDF downloads should now work!")
    
except Exception as e:
    print(f"❌ Error patching file: {e}")