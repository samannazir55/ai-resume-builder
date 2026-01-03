import React from 'react';
import { useNavigate } from 'react-router-dom';
import './TemplateSelector.css';

const TemplateSelector = ({ templates, activeTemplateId, setActiveTemplateId, userIsPremium }) => {
  const navigate = useNavigate();
  // Filter for the carousel: Free OR already active premium ones (if user unlocked them)
  // For simplicty: Just free + specific Button
  const freeTemplates = templates.filter(t => !t.is_premium);

  return (
    <div className="template-selector-container">
      <div className="template-grid">
        {freeTemplates.map((template) => (
          <div
            key={template.id}
            className={`template-card ${template.id === activeTemplateId ? 'active' : ''}`}
            onClick={() => setActiveTemplateId(template.id)}
          >
            <div className="template-preview-image">
              <span>{template.name.charAt(0)}</span>
            </div>
            <p className="template-name">{template.name}</p>
          </div>
        ))}
        
        {/* THE CALL TO ACTION BUTTON */}
        <div className="template-card special-store-card" onClick={() => navigate('/store')}>
            <div className="template-preview-image" style={{background: '#333', color:'#FFF'}}>+</div>
            <p className="template-name">Browse Premium ({templates.filter(t=>t.is_premium).length})</p>
        </div>
      </div>
    </div>
  );
};
export default TemplateSelector;
