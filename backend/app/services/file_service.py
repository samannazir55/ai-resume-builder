import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    # 1. SETUP DEFAULTS
    # We strip hash symbols so we have clean hex strings like "2c3e50"
    def clean_hex(val, default):
        if not val: return default
        s = str(val).strip().replace('#', '').replace('"', '').replace("'", "")
        return s if len(s) in [3,6] else default

    accent_hex = clean_hex(cv_data.get('accentColor') or cv_data.get('accent_color'), "2c3e50")
    text_hex = clean_hex(cv_data.get('textColor') or cv_data.get('text_color'), "333333")
    
    font_name = cv_data.get('fontFamily') or cv_data.get('font_family') or "sans-serif"
    # CSS Font strings usually need quotes if they have spaces "Times New Roman"
    if " " in font_name and "'" not in font_name and '"' not in font_name:
        font_name = f"'{font_name}'"

    # 2. RENDER PYSTACHE FIRST (Fills text variables)
    # This processes things like {{email}}, but might leave styling alone if hardcoded
    # We prep data with proper formatting for experience
    render_data = {**cv_data}
    render_data['experience'] = (render_data.get('experience') or '').replace('\n', '<br/>')
    render_data['education'] = (render_data.get('education') or '').replace('\n', '<br/>')
    
    html_content = pystache.render(template_html, render_data)
    css_content = pystache.render(template_css, render_data)

    # 3. PYTHON CSS COMPILER (Hard Swap Logic)
    # Instead of asking Weasyprint to understand vars, we do it ourselves.
    
    # Mapping table for substitutions
    replacements = {
        'var(--primary)': f"#{accent_hex}",
        'var(--primary, #2c3e50)': f"#{accent_hex}", # Common default fallback
        'var(--text-color)': f"#{text_hex}",
        'var(--text)': f"#{text_hex}",
        'var(--font)': font_name,
        'var(--font, sans-serif)': font_name
    }
    
    for var_key, value in replacements.items():
        css_content = css_content.replace(var_key, value)

    # 4. SAFETY CLEANUP REGEX
    # Just in case some manual #{{val}} existed
    # Fix double hashes ##ABC -> #ABC
    css_content = re.sub(r'#+#', '#', css_content)
    
    # Fix empty color declaration like "color: #;" -> "color: #000000;"
    css_content = re.sub(r':\s*#;', ':#000000;', css_content)
    
    # Remove CSS Root definition block entirely to avoid conflicts
    # Regex to remove :root { ... }
    css_content = re.sub(r':root\s*\{[^}]*\}', '', css_content)

    # 5. GENERATE PDF
    try:
        # Prepend the global rule for body as a safety net
        header_css = f"body {{ color: #{text_hex} !important; font-family: {font_name} !important; }}"
        full_css = header_css + "\n" + css_content
        
        doc = HTML(string=html_content)
        style = CSS(string=full_css)
        return doc.write_pdf(stylesheets=[style], presentational_hints=True)
        
    except Exception as e:
        print(f"WeasyPrint Failed: {e}")
        # Send debugging page as PDF so you can read the error instead of crashing
        err_msg = f"<h1>PDF Error</h1><p>Type: {type(e).__name__}</p><p>{str(e)}</p>"
        return HTML(string=err_msg).write_pdf()

def create_docx_from_data(cv_data: dict) -> bytes:
    document = docx.Document()
    
    # Basic DOCX Generation
    document.add_heading(cv_data.get('fullName') or cv_data.get('full_name') or 'Candidate', 0)
    contact = f"{cv_data.get('email','')} | {cv_data.get('phone','')}"
    document.add_paragraph(contact)
    
    # Render sections safely
    sections = ['summary', 'experience', 'education', 'skills']
    for section in sections:
        # Check standard camelCase keys or snake_case keys from AI
        content = cv_data.get(section) or cv_data.get(f'suggested_{section}') or cv_data.get(f'{section}_points')
        
        if content:
            document.add_heading(section.capitalize(), level=1)
            if isinstance(content, list):
                for item in content: document.add_paragraph(str(item), style='List Bullet')
            else:
                # Basic string cleanup
                text = str(content).replace('<br/>','\n').replace('<ul>','').replace('</ul>','').replace('<li>','• ').replace('</li>','\n')
                for line in text.split('\n'):
                    if line.strip(): document.add_paragraph(line.strip())

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()
