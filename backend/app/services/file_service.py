import pystache
from weasyprint import HTML, CSS
import io
import docx
import re

def ensure_clean_hex(color_value, default_hex="333333"):
    """
    Returns a clean 6-character HEX string WITHOUT the # prefix.
    This is for data that will be rendered into templates that have #{{color}}.
    
    Examples:
        "#2c3e50" -> "2c3e50"
        "2c3e50"  -> "2c3e50"
        "invalid" -> "333333" (default)
    """
    if not color_value:
        return default_hex

    # Convert to string and strip whitespace
    s = str(color_value).strip()
    
    # Remove # if present
    clean_hex = s.lstrip("#")

    # Validate (3 or 6 hex chars only)
    if re.fullmatch(r"[0-9a-fA-F]{3}|[0-9a-fA-F]{6}", clean_hex):
        # Expand 3-char hex to 6-char if needed (e.g., "abc" -> "aabbcc")
        if len(clean_hex) == 3:
            clean_hex = ''.join([c*2 for c in clean_hex])
        return clean_hex

    # If invalid (like "rgba(...)" or garbage), return default
    return default_hex

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    """
    Renders CV template with Mustache and generates PDF using WeasyPrint.
    
    CRITICAL: Templates should have CSS like:
        --primary: #{{accent_color}};
    
    And we pass accent_color WITHOUT the # (e.g., "2c3e50").
    """
    print("=" * 80)
    print("🔄 PDF GENERATION STARTING")
    print("=" * 80)
    
    # 1. Extract and Clean Colors (NO # prefix - templates add it)
    accent = ensure_clean_hex(
        cv_data.get('accentColor') or cv_data.get('accent_color'), 
        "2c3e50"
    )
    text_col = ensure_clean_hex(
        cv_data.get('textColor') or cv_data.get('text_color'), 
        "333333"
    )
    
    # 2. Extract and Sanitize Font
    font_name = cv_data.get('fontFamily') or cv_data.get('font_family') or "sans-serif"
    font_name = re.sub(r'[;"\'#]+', '', font_name).strip()

    print(f"✅ Accent Color (clean hex): {accent}")
    print(f"✅ Text Color (clean hex): {text_col}")
    print(f"✅ Font Family: {font_name}")

    # 3. Prepare Render Data for Mustache
    render_data = {
        **cv_data,
        "accent_color": accent,      # Clean hex WITHOUT #
        "text_color": text_col,       # Clean hex WITHOUT #
        "font_family": font_name,
        # Convert newlines to <br/> for HTML rendering
        "experience": (cv_data.get('experience') or '').replace('\n', '<br/>'),
        "education": (cv_data.get('education') or '').replace('\n', '<br/>'),
        "summary": (cv_data.get('summary') or '').replace('\n', '<br/>'),
        # Handle skills array
        "skills": cv_data.get('skills') if isinstance(cv_data.get('skills'), list) else []
    }

    # Convert skills string to list if needed
    if isinstance(cv_data.get('skills'), str):
        render_data["skills"] = [s.strip() for s in cv_data.get('skills').split(',') if s.strip()]

    # 4. Render Templates with Mustache
    try:
        print("\n🔨 Rendering HTML...")
        compiled_html = pystache.render(template_html, render_data)
        
        print("🔨 Rendering CSS...")
        compiled_css = pystache.render(template_css, render_data)
        
        # 5. CSS Post-Processing (Safety Net)
        # Fix any double hashes that might have been created
        if "##" in compiled_css:
            print("⚠️  Detected double hashes in CSS. Fixing...")
            compiled_css = compiled_css.replace("##", "#")
        
        # Fix bare/orphaned hashes (should not happen with fixed templates)
        compiled_css = re.sub(r':\s*#\s*;', f': #{text_col};', compiled_css)
        compiled_css = re.sub(r':\s*#\s*\}', f': #{text_col}', compiled_css)
        
        # Fix spaces after hash
        compiled_css = re.sub(r'#\s+([0-9a-fA-F])', r'#\1', compiled_css)

        # Debug output
        print("\n📋 CSS Preview (first 200 chars):")
        print(compiled_css[:200])
        
        # 6. Generate PDF with WeasyPrint
        print("\n📄 Generating PDF with WeasyPrint...")
        doc = HTML(string=compiled_html)
        style = CSS(string=compiled_css)
        
        pdf_bytes = doc.write_pdf(stylesheets=[style], presentational_hints=True)
        
        print("✅ PDF GENERATED SUCCESSFULLY!")
        print("=" * 80)
        return pdf_bytes

    except Exception as e:
        print(f"\n❌ PDF GENERATION FAILED: {e}")
        print("=" * 80)
        
        # Generate error PDF with diagnostic info
        err_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: monospace;
                    padding: 40px;
                    background-color: #fff5f5;
                    color: #c53030;
                }}
                h1 {{
                    border-bottom: 3px solid #c53030;
                    padding-bottom: 10px;
                }}
                .error-box {{
                    background: white;
                    border: 2px solid #fc8181;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .debug-info {{
                    background: #f7fafc;
                    border-left: 4px solid #4299e1;
                    padding: 15px;
                    margin-top: 20px;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <h1>⚠️ PDF Generation Error</h1>
            <div class="error-box">
                <strong>Error Message:</strong>
                <pre>{str(e)}</pre>
            </div>
            <div class="debug-info">
                <strong>Debug Information:</strong><br/>
                • Accent Color: {accent}<br/>
                • Text Color: {text_col}<br/>
                • Font Family: {font_name}<br/>
                <br/>
                <strong>Common Fixes:</strong><br/>
                1. Check that CSS template uses #{{{{accent_color}}}} (with hash)<br/>
                2. Verify color values are valid 6-char hex codes<br/>
                3. Run /api/setup_production to resync templates
            </div>
        </body>
        </html>
        """
        try:
            return HTML(string=err_html).write_pdf()
        except:
            # Absolute fallback
            return b"PDF Generation Failed - See Server Logs"


def create_docx_from_data(cv_data: dict) -> bytes:
    """
    Creates a Word document from CV data.
    Simpler format, no styling complexity.
    """
    document = docx.Document()
    
    # Header
    document.add_heading(cv_data.get('fullName', 'Candidate'), 0)
    document.add_paragraph(f"{cv_data.get('email','')} | {cv_data.get('phone','')}")
    
    # Sections
    sections = ['summary', 'experience', 'education', 'skills']
    for sec in sections:
        val = cv_data.get(sec, "")
        if val:
            document.add_heading(sec.capitalize(), 1)
            
            # Handle lists
            if isinstance(val, list):
                val = ", ".join(val)
            
            # Clean HTML tags
            clean = str(val).replace("<br/>", "\n").replace("<ul>","").replace("</ul>","")
            clean = clean.replace("<li>", "• ").replace("</li>", "\n")
            clean = re.sub(r'<[^>]+>', '', clean)  # Remove all remaining tags
            
            # Add paragraphs
            for line in clean.split('\n'):
                if line.strip(): 
                    document.add_paragraph(line.strip())

    # Save to bytes
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream.read()