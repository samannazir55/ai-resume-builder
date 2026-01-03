import pystache
from weasyprint import HTML, CSS
import io
import docx
import re
import traceback

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    # 1. SETUP DEFAULTS
    def clean_hex(val, default):
        if not val: return default
        # Remove anything that isn't a hex char
        s = str(val).strip().replace('#', '').replace('"', '').replace("'", "")
        return s if len(s) in [3,6] else default

    accent_hex = clean_hex(cv_data.get('accentColor') or cv_data.get('accent_color'), "2c3e50")
    text_hex = clean_hex(cv_data.get('textColor') or cv_data.get('text_color'), "333333")
    font_name = cv_data.get('fontFamily') or "sans-serif"

    # 2. RENDER CONTENT
    render_data = {**cv_data}
    render_data['experience'] = (render_data.get('experience') or '').replace('\n', '<br/>')
    render_data['education'] = (render_data.get('education') or '').replace('\n', '<br/>')
    
    html_content = pystache.render(template_html, render_data)
    
    # 3. CSS "HARD" COMPILATION
    # Manually injecting vars to avoid any CSS variable parser issues
    
    css_content = template_css
    
    # Simple replace logic
    replacements = {
        'var(--primary)': f"#{accent_hex}",
        'var(--text-color)': f"#{text_hex}",
        'var(--text)': f"#{text_hex}",
        'var(--font)': font_name,
        # Legacy template compatibility (Handle hardcoded template logic)
        '{{accent_color}}': accent_hex,
        '#{{accent_color}}': f"#{accent_hex}"
    }
    
    for key, val in replacements.items():
        css_content = css_content.replace(key, val)

    # FINAL CLEANUP REGEX
    # Fix double hash '##'
    css_content = re.sub(r'#+#', '#', css_content)
    # Fix empty color declaration like ': #;'
    css_content = re.sub(r':\s*#;', ':#000000;', css_content)

    # 4. GENERATION ATTEMPT
    try:
        # Prepend Reset
        full_css = f"body {{ font-family: {font_name}; color: #{text_hex}; }}\n" + css_content
        
        doc = HTML(string=html_content)
        style = CSS(string=full_css)
        return doc.write_pdf(stylesheets=[style], presentational_hints=True)
        
    except Exception as e:
        print(f"CRITICAL PDF FAILURE: {e}")
        
        # 🚨 X-RAY MODE 🚨
        # Create a visible debug report inside the PDF so we can read it.
        
        debug_html = f"""
        <html>
        <body style="font-family: monospace; padding: 20px; color: #333;">
            <h1 style="color: red; border-bottom: 2px solid red;">PDF CRASH REPORT</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><strong>Location hint:</strong> {traceback.format_exc().splitlines()[-1]}</p>
            
            <hr>
            
            <h3>🔎 THE OFFENDING CSS CODE:</h3>
            <pre style="background: #f4f4f4; padding: 10px; border: 1px solid #ccc; white-space: pre-wrap; word-wrap: break-word;">
            {add_line_numbers(full_css)}
            </pre>
        </body>
        </html>
        """
        # Fallback PDF generator (Empty CSS to ensure it renders)
        try:
            return HTML(string=debug_html).write_pdf()
        except:
            return b"Fatal Error generating Debug PDF."

def add_line_numbers(text):
    lines = text.split('\n')
    numbered = []
    for i, line in enumerate(lines):
        # Format: "  81 | .sidebar { background: #.... }"
        numbered.append(f"{i+1:4d} | {line}")
    return "\n".join(numbered)

def create_docx_from_data(cv_data: dict) -> bytes:
    document = docx.Document()
    document.add_heading(cv_data.get('fullName') or 'Candidate', 0)
    
    sections = ['summary', 'experience', 'education', 'skills']
    for section in sections:
        val = cv_data.get(section, "")
        if val:
            document.add_heading(section.capitalize(), 1)
            # Remove html tags
            clean = str(val).replace("<br/>", "\n").replace("<ul>","").replace("</ul>","").replace("<li>", "- ")
            for line in clean.split('\n'):
                if line.strip(): document.add_paragraph(line.strip())

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()
