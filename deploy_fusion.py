import os

app_jsx_path = "frontend/src/App.jsx"

app_code = """import { useState, useEffect, useRef } from 'react'; // Added useRef
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './context/useAuth';
import api, { getTemplates, createCV } from './services/api';
import './App.css';
import CVForm from './components/CVForm';
import CVPreview from './components/CVPreview';
import TemplateSelector from './components/TemplateSelector';
import ThemeToolbar from './components/ThemeToolbar';

function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  
  // STATE
  const [cvData, setCvData] = useState({
      fullName: '', email: '', phone: '', jobTitle: '', summary: '',
      experience: '', education: '', skills: '',
      accentColor: '#2c3e50', textColor: '#333333', fontFamily: 'Helvetica, Arial, sans-serif'
  });
  
  const [templates, setTemplates] = useState([]); 
  const [activeTemplateId, setActiveTemplateId] = useState('modern');
  const [cvId, setCvId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // Use a Ref to track if we have force-loaded an ID to prevent overrides
  const hasLoadedInitialId = useRef(false);

  // 1. DATA LOAD ENGINE
  useEffect(() => {
      let incoming = null;
      try {
          const s = sessionStorage.getItem('aiResult');
          if (s && s !== 'undefined') incoming = JSON.parse(s);
      } catch (e) { sessionStorage.removeItem('aiResult'); }

      if (!incoming) incoming = location.state?.generatedContent;
      if (!incoming) incoming = location.state?.existingCV;
      
      // Check for forced template via store navigation
      if (location.state?.forceTemplate) {
          console.log("💎 Forced Template via Store:", location.state.forceTemplate);
          setActiveTemplateId(location.state.forceTemplate);
          hasLoadedInitialId.current = true;
      }

      const aiData = (incoming && incoming.data) ? incoming.data : incoming;

      if (aiData) {
          console.log("📥 Editor Loading:", aiData);
          const processExp = (val) => Array.isArray(val) ? val.map(p => `• ${p}`).join('\\n') : (val || '');
          const processSkill = (val) => Array.isArray(val) ? val.join(', ') : (val || '');

          setCvData(prev => ({
              ...prev,
              fullName: aiData.full_name || user?.fullName || prev.fullName,
              email: aiData.email || user?.email || prev.email,
              phone: aiData.phone || prev.phone,
              jobTitle: aiData.desired_job_title || prev.jobTitle,
              summary: aiData.professional_summary || prev.summary,
              education: aiData.education_formatted || prev.education,
              experience: processExp(aiData.experience_points || aiData.experience),
              skills: processSkill(aiData.suggested_skills || aiData.skills),
              accentColor: aiData.accentColor || prev.accentColor,
              textColor: aiData.textColor || prev.textColor,
              fontFamily: aiData.fontFamily || prev.fontFamily
          }));
          
          if (aiData.id) setCvId(aiData.id);
          
          // IMPORTANT: If CV has a template, respect it (unless forced via Store)
          if (aiData.template_id && !location.state?.forceTemplate) {
              setActiveTemplateId(aiData.template_id);
              hasLoadedInitialId.current = true;
          }
      } else if (user && !cvData.fullName) {
          setCvData(prev => ({...prev, fullName: user.fullName || '', email: user.email || ''}));
      }
  }, [user, location.state]);

  // 2. LOAD TEMPLATE LIST (Fixed logic to prevent overwrite)
  useEffect(() => {
    getTemplates().then(data => {
        setTemplates(data);
        // Only set default to modern IF we haven't already loaded a specific ID
        if (data.length > 0 && !hasLoadedInitialId.current && activeTemplateId === 'modern') {
             // Do nothing, let state hold default 'modern'. 
             // We avoid setActiveTemplateId here to prevent overriding hooks.
        }
    }).catch(console.error);
  }, []); // Run once on mount

  const handleSave = async (silent=false) => {
      if(!user) return alert("Log in to save.");
      setIsSaving(true);
      try {
          const payload = {
            title: `Resume - ${cvData.jobTitle || 'New'}`,
            template_id: activeTemplateId,
            data: { ...cvData }
          };
          const res = await createCV(payload);
          setCvId(res.id);
          if (!silent) alert(`✅ CV Saved! ID: ${res.id}`);
          setIsSaving(false);
          return res.id;
      } catch (err) {
          if (!silent) alert("Save Failed.");
          setIsSaving(false);
          return null;
      }
  };

  if(loading) return <div>Loading...</div>;

  return (
    <div className="App">
      <header className="app-main-header">
        <div style={{display:'flex', alignItems:'center', justifyContent:'center', position:'relative'}}>
            <button onClick={() => window.location.href='/dashboard'} className="back-dash-btn">
                ⬅ Dashboard
            </button>
            <h1>AI Powered CV Builder</h1>
        </div>
        <div style={{overflowX: 'auto', paddingBottom: '5px'}}>
            <TemplateSelector
                templates={templates}
                activeTemplateId={activeTemplateId}
                setActiveTemplateId={setActiveTemplateId}
                onOpenStore={() => navigate('/store')} 
            />
        </div>
      </header>
      
      <div className="editor-layout-grid">
        <div className="form-stack" style={{display:'flex', flexDirection:'column', gap:'20px'}}>
           <ThemeToolbar data={cvData} setData={setCvData} />
           <CVForm data={cvData} setData={setCvData} customSave={()=>handleSave(false)} isSaving={isSaving} />
        </div>
        <div className="preview-stack">
           <CVPreview data={cvData} activeTemplateId={activeTemplateId} cvId={cvId} onAutoSaveRequest={()=>handleSave(true)} />
        </div>
      </div>
    </div>
  );
}
export default App;
"""

# Include new CSS for that dashboard button just in case
extra_css = """
.back-dash-btn {
    position: absolute; left: 0; 
    padding: 8px 16px; background: rgba(255,255,255,0.2); 
    border: 1px solid rgba(255,255,255,0.4); 
    color: white; border-radius: 6px; 
    cursor: pointer; font-weight: 500; font-size: 0.9rem;
    display: flex; align-items: center; gap: 5px;
    transition: 0.2s;
}
.back-dash-btn:hover { background: rgba(255,255,255,0.3); }
"""

try:
    with open(app_jsx_path, "w", encoding="utf-8") as f:
        f.write(app_code)
    
    with open("frontend/src/App.css", "a", encoding="utf-8") as f:
        f.write(extra_css)
        
    print("✅ App.jsx Patch: Fixed the 'Modern Reset' bug.")
    print("   If you select 'Ivy League' in store, it will STAY selected in editor.")

except Exception as e:
    print(f"❌ Error: {e}")