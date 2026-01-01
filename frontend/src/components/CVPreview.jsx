import React, { useState, useEffect } from 'react';
import Mustache from 'mustache';
import api from '../services/api';
// We don't import CVPreview.css here to avoid conflicts, usage is inline/scoped below

const CVPreview = ({ data, activeTemplateId, cvId, onAutoSaveRequest }) => {
  const [activeTemplate, setActiveTemplate] = useState({ html_content: "", css_styles: "" });
  const [isDown, setIsDown] = useState(false);

  useEffect(() => {
    // If you don't have this endpoint, ensure you have the activeTemplate passed as prop instead
    if (activeTemplateId) {
        api.get(`/templates/${activeTemplateId}`)
           .then(res => setActiveTemplate(res.data))
           .catch(() => console.warn("Could not load specific template logic."));
    }
  }, [activeTemplateId]);

  // 1. CRITICAL FIX: Data Mapping (Frontend camelCase -> Template snake_case)
  const pData = {
    ...data, // Keep original data accessible
    
    // Explicit mappings for Mustache
    full_name: data.fullName || "Your Name",
    job_title: data.jobTitle || "Job Title",
    email: data.email || "",
    phone: data.phone || "",
    location: data.location || "",
    
    // Logic for Initials Avatar
    full_name_initials: (data.fullName || "YN").split(' ').map(n=>n[0]).slice(0,2).join(""),
    
    // Formatting for display
    summary: data.summary,
    experience: (data.experience || '').replace(/\n/g, '<br/>'),
    education: (data.education || '').replace(/\n/g, '<br/>'),
    // Ensure skills is always an array for {{#skills}}
    skills: Array.isArray(data.skills) ? data.skills : (data.skills||'').split(',').filter(s=>s.trim()),

    // CSS Variables for coloring
    accent_color: data.accentColor || '#2c3e50',
    text_color: data.textColor || '#333333',
    font_family: data.fontFamily || 'sans-serif'
  };

  let htmlContent = "";
  let scopedCss = "";

  if (activeTemplate && activeTemplate.html_content) {
    try {
        // Render the HTML content structure
        htmlContent = Mustache.render(activeTemplate.html_content, pData);

        // 2. CRITICAL FIX: CSS Scoping
        // We define the variables on our specific container ID (#cv-preview-iso), not on :root or body.
        // We render the template's CSS, inserting values into the {{accent_color}} placeholders.
        const renderedTemplateCss = Mustache.render(activeTemplate.css_styles || "", pData);
        
        scopedCss = `
          /* Define variables LOCALLY to this container */
          #cv-preview-iso { 
            --primary: ${pData.accent_color};
            --text-main: ${pData.text_color};
            --font-main: ${pData.font_family};
            
            /* Apply generic defaults only within this box */
            font-family: var(--font-main);
            color: var(--text-main);
            width: 100%;
            height: 100%;
            overflow-y: auto;
            background: white; /* Simulate paper */
            position: relative;
          }
          
          /* Combine with Template's CSS */
          ${renderedTemplateCss}
        `;
    } catch (e) {
        console.error("Template Render Error:", e);
    }
  }

  const handleDownload = async (type) => {
      setIsDown(true);
      try {
          // Trigger save first to ensure DB has latest data
          let id = cvId;
          if (onAutoSaveRequest) { 
              // Wait for ID to come back from save
              const savedId = await onAutoSaveRequest(true); 
              if(savedId) id = savedId;
          }

          if(!id) {
            alert("Could not save CV to generate file.");
            return;
          }
          
          const response = await api.get(`/cvs/${id}/export/${type}`, { responseType: 'blob' });
          
          // Helper to download blob
          const blob = new Blob([response.data], { type: response.headers['content-type'] });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `${data.fullName || 'resume'}.${type === 'pdf' ? 'pdf' : 'docx'}`);
          document.body.appendChild(link);
          link.click();
          link.parentNode.removeChild(link);
      } catch (err) {
          console.error(err);
          // Handling fallback: backend might return HTML if PDF engine is missing
          alert("Download failed. If using PDF on Windows without GTK, this may not be supported directly. Try printing the page instead.");
      } finally { 
          setIsDown(false); 
      }
  };

  return (
    <div className="preview-panel" style={{height: '100%', display: 'flex', flexDirection: 'column'}}>
      <div className="toolbar" style={{ padding: '10px', background: '#f8f9fa', borderBottom: '1px solid #ddd', textAlign: 'right' }}>
         <span style={{marginRight: '10px', fontSize: '0.9em', color: '#666'}}>Auto-updates on change</span>
         <button onClick={() => handleDownload('pdf')} disabled={isDown} style={{marginRight: '5px'}}>
            {isDown ? '...' : 'Download PDF'}
         </button>
         <button onClick={() => handleDownload('docx')} disabled={isDown}>
            Download DOCX
         </button>
      </div>

      {/* 
         This wrapper isolates styles. 
         Any template CSS usually targets class names, so putting it inside an ID works as an encapsulation.
       */}
      <div style={{ flex: 1, background: '#555', padding: '20px', overflow: 'hidden' }}>
         <div 
            id="cv-preview-iso" 
            className="cv-paper" 
            style={{ 
                background: 'white', 
                boxShadow: '0 0 10px rgba(0,0,0,0.3)', 
                minHeight: '100%' 
            }}
         >
            <style>{scopedCss}</style>
            <div dangerouslySetInnerHTML={{__html: htmlContent}} />
         </div>
      </div>
    </div>
  );
};

export default CVPreview;