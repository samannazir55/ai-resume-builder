import React, { useState } from 'react';
import { useAuth } from '../context/useAuth';
import api from '../services/api';
import './AdminPage.css';

const AdminPage = () => {
  const { user } = useAuth();
  
  // State for the new template
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    html_content: '',
    css_styles: '',
    is_premium: false,
    category: 'modern'
  });
  const [status, setStatus] = useState('');
  const [warnings, setWarnings] = useState([]);

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
    
    // Clear warnings when user edits
    if (e.target.name === 'css_styles') {
      setWarnings([]);
    }
  };

  // 🔥 AUTO-FIX CSS: Add # to color variables
  const fixColorVariables = (css) => {
    let fixed = css;
    const fixes = [];
    
    // Fix missing # in CSS custom properties
    if (css.includes('{{accent_color}}') && !css.includes('#{{accent_color}}')) {
      fixed = fixed.replace(/:\s*{{accent_color}}/g, ': #{{accent_color}}');
      fixes.push('✅ Added # to accent_color');
    }
    
    if (css.includes('{{text_color}}') && !css.includes('#{{text_color}}')) {
      fixed = fixed.replace(/:\s*{{text_color}}/g, ': #{{text_color}}');
      fixes.push('✅ Added # to text_color');
    }
    
    // Fix any bare color references in properties
    fixed = fixed.replace(/color:\s*{{accent_color}}/g, 'color: #{{accent_color}}');
    fixed = fixed.replace(/background:\s*{{accent_color}}/g, 'background: #{{accent_color}}');
    fixed = fixed.replace(/border:\s*{{accent_color}}/g, 'border: #{{accent_color}}');
    fixed = fixed.replace(/color:\s*{{text_color}}/g, 'color: #{{text_color}}');
    
    return { fixed, fixes };
  };

  // 🔍 VALIDATE TEMPLATE
  const validateTemplate = () => {
    const warns = [];
    const { html_content, css_styles } = formData;
    
    // Check for required Mustache variables
    const requiredVars = ['{{full_name}}', '{{job_title}}', '{{email}}', '{{phone}}'];
    requiredVars.forEach(varName => {
      if (!html_content.includes(varName)) {
        warns.push(`⚠️ Missing ${varName} in HTML`);
      }
    });
    
    // Check for color variables in CSS
    if (!css_styles.includes('{{accent_color}}') && !css_styles.includes('{{text_color}}')) {
      warns.push('⚠️ No color variables found. Consider using {{accent_color}} and {{text_color}}');
    }
    
    // Check for # before color variables
    if (css_styles.includes('{{accent_color}}') && !css_styles.includes('#{{accent_color}}')) {
      warns.push('🔧 Missing # before {{accent_color}} - will auto-fix on publish');
    }
    if (css_styles.includes('{{text_color}}') && !css_styles.includes('#{{text_color}}')) {
      warns.push('🔧 Missing # before {{text_color}} - will auto-fix on publish');
    }
    
    // Suggest custom fields
    const customFields = ['{{hobbies}}', '{{languages}}', '{{certifications}}', '{{location}}'];
    const hasCustomFields = customFields.some(field => html_content.includes(field));
    if (!hasCustomFields) {
      warns.push('💡 Tip: Consider adding custom fields like {{hobbies}}, {{languages}}, {{certifications}} for richer CVs');
    }
    
    return warns;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Validating...');
    
    // Validate first
    const validationWarnings = validateTemplate();
    setWarnings(validationWarnings);
    
    // Auto-fix CSS
    const { fixed: fixedCSS, fixes } = fixColorVariables(formData.css_styles);
    
    if (fixes.length > 0) {
      setStatus('Auto-fixing CSS...');
      console.log('🔧 Applied fixes:', fixes);
    }
    
    setStatus('Publishing...');
    
    try {
      const payload = {
        ...formData,
        css_styles: fixedCSS  // Use auto-fixed CSS
      };
      
      await api.post('/admin/templates', payload);
      setStatus('✅ Published Successfully! Template is now Live.');
      
      // Update form to show fixed CSS
      setFormData(prev => ({ ...prev, css_styles: fixedCSS }));
      
      // Clear form after 2 seconds
      setTimeout(() => {
        setFormData({
          id: '',
          name: '',
          html_content: '',
          css_styles: '',
          is_premium: false,
          category: 'modern'
        });
        setStatus('');
        setWarnings([]);
      }, 2000);
      
    } catch (err) {
      setStatus(`❌ Error: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handlePreview = () => {
    const warns = validateTemplate();
    setWarnings(warns);
    setStatus(warns.length === 0 ? '✅ Validation passed!' : '⚠️ See warnings below');
  };

  if (!user) return <div className="admin-container">Please Login.</div>;

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🛠️ Template Factory</h1>
        <p>Paste your ChatGPT code here to launch a new design instantly.</p>
        <button 
          type="button" 
          onClick={handlePreview} 
          className="validate-btn"
          style={{
            padding: '8px 16px',
            background: '#3498db',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
        >
          🔍 Validate Template
        </button>
      </div>

      {warnings.length > 0 && (
        <div className="warnings-box" style={{
          background: '#fff3cd',
          border: '1px solid #ffc107',
          padding: '15px',
          borderRadius: '4px',
          margin: '20px 0'
        }}>
          <h4 style={{margin: '0 0 10px 0'}}>⚠️ Validation Warnings:</h4>
          <ul style={{margin: 0, paddingLeft: '20px'}}>
            {warnings.map((warn, idx) => (
              <li key={idx}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      <form onSubmit={handleSubmit} className="admin-grid">
        <div className="admin-sidebar">
          <div className="form-group">
             <label>Template ID (unique)</label>
             <input 
               name="id" 
               value={formData.id} 
               onChange={handleChange} 
               placeholder="creative_orange" 
               pattern="[a-z_]+"
               title="Only lowercase letters and underscores"
               required 
             />
             <small style={{color: '#666', fontSize: '12px'}}>Use lowercase with underscores (e.g., modern_blue)</small>
          </div>
          
          <div className="form-group">
             <label>Display Name</label>
             <input 
               name="name" 
               value={formData.name} 
               onChange={handleChange} 
               placeholder="Creative Orange" 
               required 
             />
          </div>
          
          <div className="form-group">
             <label>Category</label>
             <select name="category" value={formData.category} onChange={handleChange}>
                 <option value="modern">Modern</option>
                 <option value="professional">Professional</option>
                 <option value="creative">Creative</option>
                 <option value="academic">Academic</option>
                 <option value="technical">Technical</option>
             </select>
          </div>
          
          <div className="form-group checkbox-group">
             <label>
               <input 
                 type="checkbox" 
                 name="is_premium" 
                 checked={formData.is_premium} 
                 onChange={handleChange} 
               />
               Is Premium? 💎
             </label>
          </div>
          
          <button type="submit" className="publish-btn">🚀 Publish Live</button>
          <div className="status-msg">{status}</div>
          
          {/* Quick Reference */}
          <div style={{
            marginTop: '20px',
            padding: '10px',
            background: '#f8f9fa',
            borderRadius: '4px',
            fontSize: '12px'
          }}>
            <strong>📋 Available Variables:</strong>
            <div style={{marginTop: '5px', fontFamily: 'monospace'}}>
              {`{{full_name}}, {{job_title}}`}<br/>
              {`{{email}}, {{phone}}, {{location}}`}<br/>
              {`{{summary}}, {{experience}}, {{education}}`}<br/>
              {`{{#skills}}...{{/skills}}`}<br/>
              {`{{#hobbies}}...{{/hobbies}}`}<br/>
              {`{{#languages}}...{{/languages}}`}<br/>
              {`{{#certifications}}...{{/certifications}}`}<br/>
              {`{{linkedin}}, {{github}}, {{portfolio}}`}<br/>
              <br/>
              <strong>Colors (auto-fixed):</strong><br/>
              {`{{accent_color}}, {{text_color}}`}
            </div>
          </div>
        </div>

        <div className="admin-code-area">
          <div className="code-box">
             <label>HTML (Mustache Format)</label>
             <textarea 
               name="html_content" 
               value={formData.html_content} 
               onChange={handleChange} 
               placeholder="<div class='resume-modern'>
  <div class='sidebar'>
    <h1>{{full_name}}</h1>
    <p>{{job_title}}</p>
    {{#skills}}<li>{{.}}</li>{{/skills}}
  </div>
</div>" 
               required 
               style={{fontFamily: 'monospace', fontSize: '13px'}}
             />
          </div>
          
          <div className="code-box">
             <label>CSS (will auto-fix color variables)</label>
             <textarea 
               name="css_styles" 
               value={formData.css_styles} 
               onChange={handleChange} 
               placeholder=":root { --primary: #{{accent_color}}; }
.resume-modern { 
  font-family: sans-serif; 
  color: #{{text_color}};
}" 
               required 
               style={{fontFamily: 'monospace', fontSize: '13px'}}
             />
          </div>
        </div>
      </form>
    </div>
  );
};

export default AdminPage;