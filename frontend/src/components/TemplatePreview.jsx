import React, { useState, useEffect } from 'react';
import Mustache from 'mustache';

// Mock data for previews - looks professional but clearly sample data
const MOCK_CV_DATA = {
  full_name: "Alex Johnson",
  job_title: "Senior Product Designer",
  email: "alex.johnson@email.com",
  phone: "+1 (555) 123-4567",
  location: "San Francisco, CA",
  full_name_initials: "AJ",
  
  summary: "Creative product designer with 8+ years of experience crafting user-centered digital experiences. Passionate about solving complex problems through elegant design solutions.",
  
  experience: `• Led design system overhaul for 50+ components, reducing design debt by 60%
• Collaborated with cross-functional teams to ship 3 major product features
• Mentored junior designers and established design critique processes`,
  
  education: `Bachelor of Fine Arts in Graphic Design
Rhode Island School of Design, 2015`,
  
  skills: ["Figma", "Sketch", "User Research", "Prototyping", "Design Systems", "HTML/CSS"],
  
  languages: ["English (Native)", "Spanish (Fluent)", "French (Basic)"],
  hobbies: ["Photography", "Hiking", "Coffee Brewing", "Reading"],
  certifications: ["Google UX Design Certificate", "Interaction Design Foundation"],
  
  linkedin: "linkedin.com/in/alexjohnson",
  github: "github.com/alexjohnson",
  portfolio: "alexjohnson.design",
  
  // Colors
  accent_color: "2c3e50",
  text_color: "333333",
  font_family: "sans-serif"
};

const TemplatePreview = ({ template, scale = 0.5, showLabel = false }) => {
  const [renderedHTML, setRenderedHTML] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!template || !template.html_content) {
      setRenderedHTML('<div style="padding:20px;text-align:center;color:#999;">No template data</div>');
      return;
    }

    try {
      // Strip hash from colors for template
      const stripHash = (color) => {
        if (!color) return '333333';
        return String(color).replace(/#/g, '');
      };

      const previewData = {
        ...MOCK_CV_DATA,
        accent_color: stripHash(template.accent_color || MOCK_CV_DATA.accent_color),
        text_color: stripHash(template.text_color || MOCK_CV_DATA.text_color)
      };

      // Render HTML
      const htmlContent = Mustache.render(template.html_content, previewData);
      
      // Render CSS with # prefix
      let templateCss = template.css_styles || "";
      templateCss = templateCss.replace(/:\s*{{accent_color}}/g, ': #{{accent_color}}');
      templateCss = templateCss.replace(/:\s*{{text_color}}/g, ': #{{text_color}}');
      const renderedCss = Mustache.render(templateCss, previewData);

      const fullHTML = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
              font-family: ${previewData.font_family};
              background: white;
              overflow: hidden;
            }
            ${renderedCss}
          </style>
        </head>
        <body>
          ${htmlContent}
        </body>
        </html>
      `;

      setRenderedHTML(fullHTML);
      setError(null);
    } catch (e) {
      console.error('Preview render error:', e);
      setError(e.message);
      setRenderedHTML(`<div style="padding:20px;color:#e74c3c;">Preview Error: ${e.message}</div>`);
    }
  }, [template]);

  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      position: 'relative',
      overflow: 'hidden',
      background: '#f8f9fa'
    }}>
      {showLabel && (
        <div style={{
          position: 'absolute',
          top: 10,
          left: 10,
          background: 'rgba(0,0,0,0.7)',
          color: 'white',
          padding: '4px 12px',
          borderRadius: '4px',
          fontSize: '12px',
          fontWeight: 'bold',
          zIndex: 10
        }}>
          {template?.name || 'Template'} Preview
        </div>
      )}
      
      {error && (
        <div style={{
          position: 'absolute',
          bottom: 10,
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#fee',
          color: '#c00',
          padding: '8px 16px',
          borderRadius: '4px',
          fontSize: '11px',
          zIndex: 10
        }}>
          ⚠️ {error}
        </div>
      )}

      <iframe
        srcDoc={renderedHTML}
        title="Template Preview"
        style={{
          width: `${100 / scale}%`,
          height: `${100 / scale}%`,
          border: 'none',
          transform: `scale(${scale})`,
          transformOrigin: 'top left',
          background: 'white'
        }}
        sandbox="allow-same-origin"
      />
    </div>
  );
};

export default TemplatePreview;