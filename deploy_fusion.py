import os

# 1. UPDATE TEMPLATE STORE
# Goal: When user clicks "Unlock/Select" on a premium template, 
# CREATE a CV entry in the DB immediately so it exists.

store_path = os.path.join("frontend", "src", "components", "TemplateStore.jsx")

new_store_code = """import React, { useEffect, useState } from 'react';
import { getTemplates, createCV } from '../services/api'; // Added createCV
import { useAuth } from '../context/useAuth'; // Get user details for defaults
import { useNavigate } from 'react-router-dom';
import './TemplateStore.css';

const TemplateStore = () => {
  const [templates, setTemplates] = useState([]);
  const [processingId, setProcessingId] = useState(null); // Loading state for buttons
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    getTemplates().then(setTemplates);
  }, []);

  const handleSelect = async (tmpl) => {
      // PREVENT DOUBLE CLICK
      if (processingId) return;
      
      const isPaid = tmpl.is_premium;
      
      if (isPaid) {
          // 1. Simulate Payment Flow
          const confirmed = window.confirm(`💎 Premium Design: '${tmpl.name}'\\n\\nDo you want to unlock and use this template? (Simulated Payment)`);
          if (!confirmed) return;
      }

      setProcessingId(tmpl.id);

      try {
          // 2. AUTO-CREATE THE CV DRAFT
          // We create it in the database immediately so it appears on the Dashboard
          const defaultData = {
              title: `${tmpl.name} CV - ${new Date().toLocaleDateString()}`,
              template_id: tmpl.id,
              data: {
                  fullName: user?.fullName || 'Your Name',
                  email: user?.email || '',
                  jobTitle: 'Target Role',
                  summary: 'Ready to write my new professional summary...',
                  accentColor: '#2c3e50', // Default nice blue
                  fontFamily: 'sans-serif'
              }
          };

          console.log("creating CV draft for...", tmpl.name);
          const response = await createCV(defaultData);
          
          // 3. REDIRECT TO EDITOR with the new specific ID
          // We pass existingCV so App.jsx loads from DB immediately
          navigate('/editor', { state: { existingCV: response } });

      } catch (err) {
          alert("Error creating CV: " + err.message);
          setProcessingId(null);
      }
  };

  return (
    <div className="store-container">
        <header className="store-header">
            <button className="back-btn" onClick={() => navigate('/editor')}>⬅ Back to Editor</button>
            <button className="dash-btn" onClick={() => navigate('/dashboard')}>📂 My Dashboard</button>
            <h1>Template Gallery</h1>
            <p>Select a design to start a new Resume</p>
        </header>

        <div className="store-section">
            <h2 className="section-label">💎 Premium Collection</h2>
            <div className="store-grid">
                {templates.filter(t => t.is_premium).map(t => (
                    <div key={t.id} className="store-card" onClick={() => handleSelect(t)}>
                        <div className="card-preview premium-bg">
                            {/* Visual representation */}
                            <span style={{fontSize:'3rem'}}>✨</span>
                            <span className="premium-tag">PRO</span>
                        </div>
                        <div className="card-info">
                            <h3>{t.name}</h3>
                            <p className="category">{t.category}</p>
                            <button className="buy-btn" disabled={processingId === t.id}>
                                {processingId === t.id ? "Creating..." : "Select & Use"}
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
        
        <div className="store-section">
            <h2 className="section-label">🌱 Free Essentials</h2>
            <div className="store-grid small">
                {templates.filter(t => !t.is_premium).map(t => (
                    <div key={t.id} className="store-card free" onClick={() => handleSelect(t)}>
                        <div className="card-preview free-bg">
                            <span style={{fontSize:'3rem'}}>📄</span>
                        </div>
                        <div className="card-info">
                            <h3>{t.name}</h3>
                            <button className="buy-btn free-btn" disabled={processingId === t.id}>
                                {processingId === t.id ? "Loading..." : "Use Free"}
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    </div>
  );
};
export default TemplateStore;
"""

# 2. UPDATE CSS (For new buttons and layout)
store_css_append = """
.back-btn { 
    position: absolute; left: 30px; top: 30px; 
    background: transparent; border: 1px solid #ccc; padding: 8px 15px; borderRadius: 6px; cursor: pointer; color: #555; font-weight: bold;
}
.dash-btn { 
    position: absolute; right: 30px; top: 30px; 
    background: #2c3e50; color: white; padding: 8px 15px; borderRadius: 6px; cursor: pointer; font-weight: bold; border: none;
}
.store-header { position: relative; padding-top: 20px; }
.section-label { color: #64748b; font-size: 14px; text-transform: uppercase; margin: 30px 0 15px 0; border-bottom: 2px solid #e2e8f0; display: inline-block; }

/* Gradients for previews */
.premium-bg { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: #fbbf24; }
.free-bg { background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); color: #64748b; }

.free-btn { background: #64748b !important; }
"""

try:
    with open(store_path, "w", encoding="utf-8") as f:
        f.write(new_store_code)
    
    with open("frontend/src/components/TemplateStore.css", "a", encoding="utf-8") as f:
        f.write(store_css_append)
        
    print("✅ STORE LOGIC UPDATED.")
    print("   - Clicking any template (Free or Pro) now creates a DB Draft.")
    print("   - Draft immediately syncs to Dashboard.")
    print("   - Redirects to Editor ready to work.")

except Exception as e:
    print(f"❌ Error: {e}")