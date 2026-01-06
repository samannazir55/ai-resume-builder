import { useState, useEffect, useRef } from 'react';
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
    // NEW FIELDS
    location: '', hobbies: '', languages: '', certifications: '',
    linkedin: '', github: '', portfolio: '',
    // Styling
    accentColor: '#2c3e50', textColor: '#333333', fontFamily: 'Helvetica, Arial, sans-serif'
});
  
  const [templates, setTemplates] = useState([]); 
  const [activeTemplateId, setActiveTemplateId] = useState('modern');
  const [cvId, setCvId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // CRITICAL FIX: Track if we've already processed location.state to prevent reset
  const hasProcessedLocation = useRef(false);

  // 1. LOAD TEMPLATES FIRST (Before processing navigation state)
  useEffect(() => {
    getTemplates()
      .then(data => {
        setTemplates(data);
        console.log('✅ Templates loaded:', data.length);
      })
      .catch(err => console.error('❌ Template load error:', err));
  }, []); // Run once on mount

  // 2. PROCESS NAVIGATION STATE & DATA LOAD (With proper priority)
  useEffect(() => {
      // Prevent re-processing if we've already handled this navigation
      if (hasProcessedLocation.current) return;
      
      let incoming = null;
      try {
          const s = sessionStorage.getItem('aiResult');
          if (s && s !== 'undefined') incoming = JSON.parse(s);
      } catch (e) { 
          sessionStorage.removeItem('aiResult'); 
      }

      if (!incoming) incoming = location.state?.generatedContent;
      if (!incoming) incoming = location.state?.existingCV;
      
      // 🔥 CRITICAL FIX: Check for forced template FIRST (highest priority)
      if (location.state?.forceTemplate) {
          console.log("💎 FORCE TEMPLATE from Store:", location.state.forceTemplate);
          setActiveTemplateId(location.state.forceTemplate);
          hasProcessedLocation.current = true;
          
          // Clear the navigation state so it doesn't re-trigger
          navigate(location.pathname, { replace: true, state: {} });
          return; // Exit early, don't process other data
      }

      const aiData = (incoming && incoming.data) ? incoming.data : incoming;

      if (aiData) {
          console.log("🔥 Editor Loading Data:", aiData);
          const processExp = (val) => Array.isArray(val) ? val.map(p => `• ${p}`).join('\n') : (val || '');
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
          
          // If CV has a template, use it
          if (aiData.template_id) {
              console.log("📋 Using CV's template:", aiData.template_id);
              setActiveTemplateId(aiData.template_id);
          }
          
          hasProcessedLocation.current = true;
      } else if (user && !cvData.fullName) {
          // No incoming data, just populate with user info
          setCvData(prev => ({
              ...prev, 
              fullName: user.fullName || '', 
              email: user.email || ''
          }));
          hasProcessedLocation.current = true;
      }
  }, [location.state, user]); // Re-run when location.state or user changes

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