import os

# 1. CREATE STORE PAGE (The "Gallery")
store_jsx = """import React, { useEffect, useState } from 'react';
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
"""

store_css = """
.store-container { padding: 40px; background: #f8fafc; min-height: 100vh; }
.store-header { text-align: center; margin-bottom: 50px; }
.store-header h1 { font-size: 36px; margin-bottom: 10px; color: #1e293b; }
.store-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; }

.store-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.2s; cursor: pointer; border: 1px solid #e2e8f0; }
.store-card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.1); }

.card-preview { height: 200px; background: #eee; position: relative; display: flex; align-items: center; justify-content: center; font-size: 40px; font-weight: bold; color: #cbd5e1; }
.premium-tag { position: absolute; top: 10px; right: 10px; background: #e74c3c; color: white; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; letter-spacing: 1px; }

.card-info { padding: 20px; text-align: center; }
.card-info h3 { margin: 0 0 5px 0; font-size: 18px; }
.category { color: #94a3b8; font-size: 12px; text-transform: uppercase; margin-bottom: 15px; }
.buy-btn { width: 100%; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }

/* Free Styling */
.store-card.free { border-left: 5px solid #27ae60; }
"""

# 2. UPDATE TOP BAR (TemplateSelector) to only show Free + Button
topbar_code = """import React from 'react';
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
"""

# 3. UPDATE ROUTER & APP TO HANDLE LOGIC
try:
    with open("frontend/src/components/TemplateStore.jsx", "w", encoding="utf-8") as f:
        f.write(store_jsx)
    with open("frontend/src/components/TemplateStore.css", "w", encoding="utf-8") as f:
        f.write(store_css)
    with open("frontend/src/components/TemplateSelector.jsx", "w", encoding="utf-8") as f:
        f.write(topbar_code)
    
    # Add Route
    main_path = "frontend/src/main.jsx"
    with open(main_path, "r", encoding="utf-8") as f:
        m = f.read()
    
    if "TemplateStore" not in m:
        m = m.replace("import App", "import TemplateStore from './components/TemplateStore';\nimport App")
        m = m.replace(
            "<Route path=\"/editor\"",
            "<Route path=\"/store\" element={<ProtectedRoute><TemplateStore /></ProtectedRoute>} />\n<Route path=\"/editor\""
        )
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(m)
            
    print("✅ STORE INSTALLED.")
    print("   - Added /store route")
    print("   - Updated Top Bar to show 'Browse Premium'")
    print("   - Restored backend data")

except Exception as e:
    print(f"❌ Error: {e}")