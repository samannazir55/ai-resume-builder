import React, { useState, useEffect } from 'react';
import Mustache from 'mustache';
import api from '../services/api';

const CVPreview = ({ data, activeTemplateId, cvId, onAutoSaveRequest }) => {
  const [activeTemplate, setActiveTemplate] = useState({ html_content: "", css_styles: "" });
  const [isDown, setIsDown] = useState(false);

  useEffect(() => {
    if (activeTemplateId) {
        api.get(`/templates/${activeTemplateId}`)
           .then(res => setActiveTemplate(res.data))
           .catch(() => console.warn("Could not load template."));
    }
  }, [activeTemplateId]);

  // CRITICAL FIX: Remove # from colors - template will add it
  const stripHash = (color) => {
    if (!color) return '333333';
    return String(color).replace(/#/g, '');
  };

  // Data mapping for Mustache
  const pData = {
    ...data,
    
    // Personal info
    full_name: data.fullName || "Your Name",
    job_title: data.jobTitle || "Job Title",
    email: data.email || "",
    phone: data.phone || "",
    location: data.location || "",
    full_name_initials: (data.fullName || "YN").split(' ').map(n=>n[0]).slice(0,2).join(""),
    
    // Content
    summary: data.summary,
    experience: (data.experience || '').replace(/\n/g, '<br/>'),
    education: (data.education || '').replace(/\n/g, '<br/>'),
    skills: Array.isArray(data.skills) 
      ? data.skills 
      : (data.skills||'').split(',').map(s => s.trim()).filter(Boolean),

    // CRITICAL: Colors WITHOUT hash
    accent_color: stripHash(data.accentColor || '#2c3e50'),
    text_color: stripHash(data.textColor || '#333333'),
    font_family: data.fontFamily || 'sans-serif'
  };

  let htmlContent = "";
  let scopedCss = "";

  if (activeTemplate && activeTemplate.html_content) {
    try {
        // Render HTML
        htmlContent = Mustache.render(activeTemplate.html_content, pData);

        // Render CSS - add # before color variables
        let templateCss = activeTemplate.css_styles || "";
        
        // Ensure colors have # prefix in CSS
        templateCss = templateCss.replace(/:\s*{{accent_color}}/g, ': #{{accent_color}}');
        templateCss = templateCss.replace(/:\s*{{text_color}}/g, ': #{{text_color}}');
        
        const renderedCss = Mustache.render(templateCss, pData);
        
        scopedCss = `
          #cv-preview-iso { 
            --primary: #${pData.accent_color};
            --text-main: #${pData.text_color};
            --font-main: ${pData.font_family};
            
            font-family: var(--font-main);
            color: var(--text-main);
            width: 100%;
            height: 100%;
            overflow-y: auto;
            background: white;
            position: relative;
          }
          
          ${renderedCss}
        `;
    } catch (e) {
        console.error("Template Render Error:", e);
    }
  }

  const handleDownload = async (type) => {
      setIsDown(true);
      try {
          let id = cvId;
          if (onAutoSaveRequest) { 
              const savedId = await onAutoSaveRequest(true); 
              if(savedId) id = savedId;
          }

          if(!id) {
            alert("Could not save CV to generate file.");
            return;
          }
          
          const response = await api.get(`/cvs/${id}/export/${type}`, { responseType: 'blob' });
          
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
          alert("Download failed. Check console for details.");
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