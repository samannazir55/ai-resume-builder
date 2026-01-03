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
        
    return clean

def create_pdf_from_template(template_html: str, template_css: str, cv_data: dict) -> bytes:
    print("=" * 80)
    print("🔍 PDF GENERATION DEBUG START")
    print("=" * 80)
    
    # Get colors WITHOUT hash
    accent = ensure_single_hash(cv_data.get('accentColor') or cv_data.get('accent_color'), "2c3e50")
    text_col = ensure_single_hash(cv_data.get('textColor') or cv_data.get('text_color'), "333333")
    
    print(f"✓ Accent color (no hash): {accent}")
    print(f"✓ Text color (no hash): {text_col}")
    
    font_name = cv_data.get('fontFamily') or cv_data.get('font_family') or "sans-serif"
    font_name = re.sub(r'[;"\']+', '', font_name)
    print(f"✓ Font family: {font_name}")

    # Prepare data
    render_data = {
        **cv_data,
        "accent_color": accent,
        "text_color": text_col,
        "font_family": font_name,
        "experience": (cv_data.get('experience') or '').replace('\n', '<br/>'),
        "education": (cv_data.get('education') or '').replace('\n', '<br/>')
    }

    print("\n📝 BEFORE RENDERING:")
    print(f"Template CSS (first 300 chars):\n{template_css[:300]}")
    
    # Render
    compiled_html = pystache.render(template_html, render_data)
    compiled_css = pystache.render(template_css, render_data)

    print("\n📝 AFTER PYSTACHE RENDERING:")
    print(f"Compiled CSS (first 500 chars):\n{compiled_css[:500]}")

    # Check for problematic patterns
    double_hash_count = compiled_css.count('##')
    print(f"\n⚠️  Double hash count (##): {double_hash_count}")
    
    if double_hash_count > 0:
        print("❌ FOUND DOUBLE HASHES! Locations:")
        for i, line in enumerate(compiled_css.split('\n')[:50], 1):
            if '##' in line:
                print(f"   Line {i}: {line.strip()}")

    # Safety cleanup
    compiled_css = re.sub(r'##+', '#', compiled_css)
    compiled_css = re.sub(r':\s*#?\s*;', f': #{text_col};', compiled_css)

    print("\n📝 AFTER CLEANUP:")
    print(f"Final CSS (first 500 chars):\n{compiled_css[:500]}")

    # Check for error at position 81
    print("\n🎯 CHECKING POSITION 81:")
    if len(compiled_css) > 81:
        print(f"Characters 70-90: '{compiled_css[70:90]}'")
        print(f"Character at 81: '{compiled_css[81]}'")

    # Generate PDF
    try:
        doc = HTML(string=compiled_html)
        style = CSS(string=compiled_css)
        pdf_bytes = doc.write_pdf(stylesheets=[style], presentational_hints=True)
        print("\n✅ PDF GENERATED SUCCESSFULLY!")
        print("=" * 80)
        return pdf_bytes
        
    except Exception as e:
        print(f"\n❌ PDF GENERATION FAILED!")
        print(f"Error: {e}")
        print(f"\nFull CSS output:\n{compiled_css}")
        print("=" * 80)
        
        # Save to file for inspection
        try:
            with open('/tmp/failed_css.css', 'w') as f:
                f.write(compiled_css)
            print("💾 Failed CSS saved to /tmp/failed_css.css")
        except:
            pass
        
        # Return error PDF
        err_msg = f"""
        <html>
        <body style="font-family: monospace; padding: 20px;">
            <h1>PDF Generation Failed</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <h2>Debug Info:</h2>
            <pre>{compiled_css[:1000]}</pre>
        </body>
        </html>
        """
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