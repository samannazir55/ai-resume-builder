import React from 'react';
import './TemplateSelector.css';

const TemplateSelector = ({ templates, activeTemplateId, setActiveTemplateId, userIsPremium, onUpgradeRequest }) => {

  const handleSelect = (template) => {
    // FREEMIUM LOGIC
    if (template.is_premium && !userIsPremium) {
        if (onUpgradeRequest) onUpgradeRequest(); else alert("Upgrade required!");
        // We do NOT change the active template
        return;
    }
    setActiveTemplateId(template.id);
  };

  return (
    <div className="template-selector-container">
      <h3>Choose a Style</h3>
      <div className="template-grid">
        {templates.map((template) => (
          <div
            key={template.id}
            className={`template-card ${template.id === activeTemplateId ? 'active' : ''}`}
            onClick={() => handleSelect(template)}
          >
            {/* Show Lock if Premium */}
            {template.is_premium && !userIsPremium && (
                <div className="premium-badge" title="Premium Template">🔒</div>
            )}
            
            <div className="template-preview-image">
              <span>{template.name.charAt(0)}</span>
            </div>
            <p className="template-name">
                {template.name}
                {template.is_premium && <span style={{color:'#e74c3c', fontSize:'10px', display:'block'}}>PREMIUM</span>}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TemplateSelector;
