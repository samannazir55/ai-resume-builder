import React from 'react';
import { useNavigate } from 'react-router-dom';
import './TemplateSelector.css';

const TemplateSelector = ({ templates, activeTemplateId, setActiveTemplateId, currentData, cvId }) => {
  const navigate = useNavigate();
  
  // Only show free templates in the quick selector
  const freeTemplates = templates.filter(t => !t.is_premium);
  const premiumCount = templates.filter(t => t.is_premium).length;

  const handleBrowseClick = () => {
    // Pass current data to template store to preserve it
    navigate('/store', {
      state: {
        existingData: currentData,
        cvId: cvId
      }
    });
  };

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
        
        {/* Enhanced Call-to-Action Card */}
        <div className="template-card special-store-card" onClick={handleBrowseClick}>
          <div className="template-preview-image premium-gradient">
            <span style={{fontSize: '40px'}}>✨</span>
          </div>
          <p className="template-name">
            <strong>Browse All</strong>
            <br/>
            <span style={{fontSize: '11px', color: '#94a3b8'}}>
              {premiumCount} Premium + {freeTemplates.length} Free
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default TemplateSelector;