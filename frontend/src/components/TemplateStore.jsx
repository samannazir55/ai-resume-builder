import React, { useEffect, useState } from 'react';
import { getTemplates } from '../services/api';
import { useNavigate } from 'react-router-dom';
import './TemplateStore.css';

const TemplateStore = () => {
  const [templates, setTemplates] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    getTemplates().then(setTemplates);
  }, []);

  const handleSelect = (tmpl) => {
      // Since this is a "Store", selecting here means "I want to buy/use this"
      if (tmpl.is_premium) {
          // Open Payment Logic (For now simulated alert/modal)
          const confirmed = window.confirm(`Unlock ${tmpl.name} for $5?`);
          if (confirmed) {
              alert("Processing... Success! You unlocked Premium.");
              // Here you would redirect to editor with state { unlocked: true }
              navigate('/editor', { state: { forceTemplate: tmpl.id } });
          }
      } else {
          // It's free? Just go use it
          navigate('/editor', { state: { forceTemplate: tmpl.id } });
      }
  };

  return (
    <div className="store-container">
        <header className="store-header">
            <button onClick={() => navigate('/editor')}>⬅ Back to Editor</button>
            <h1>Premium Design Gallery</h1>
            <p>Stand out with professional designs.</p>
        </header>

        <div className="store-grid">
            {templates.filter(t => t.is_premium).map(t => (
                <div key={t.id} className="store-card" onClick={() => handleSelect(t)}>
                    <div className="card-preview">
                        <div className="preview-art">{t.name.substring(0,2)}</div>
                        <span className="premium-tag">💎 PREMIUM</span>
                    </div>
                    <div className="card-info">
                        <h3>{t.name}</h3>
                        <p className="category">{t.category}</p>
                        <button className="buy-btn">Unlock Now</button>
                    </div>
                </div>
            ))}
        </div>
        
        <div className="store-section">
            <h2>Free Designs</h2>
            <div className="store-grid small">
                {templates.filter(t => !t.is_premium).map(t => (
                    <div key={t.id} className="store-card free" onClick={() => handleSelect(t)}>
                        <div className="card-info"><h3>{t.name}</h3></div>
                    </div>
                ))}
            </div>
        </div>
    </div>
  );
};
export default TemplateStore;
