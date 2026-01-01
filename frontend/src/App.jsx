import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './context/useAuth';
import { getTemplates, createCV } from './services/api';
import './App.css';
import CVForm from './components/CVForm';
import CVPreview from './components/CVPreview';
import TemplateSelector from './components/TemplateSelector';
import ThemeToolbar from './components/ThemeToolbar';

function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  
  const [cvData, setCvData] = useState({
      fullName: '', email: '', phone: '', jobTitle: '', summary: '',
      experience: '', education: '', skills: '',
      accentColor: '#2c3e50', textColor: '#333333', fontFamily: 'sans-serif'
  });
  
  const [templates, setTemplates] = useState([]);
  const [activeTemplateId, setActiveTemplateId] = useState('modern');
  const [cvId, setCvId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
      let incoming = null;
      let originalRequest = null;
      
      try {
          const s = sessionStorage.getItem('aiResult');
          if (s && s !== 'undefined') incoming = JSON.parse(s);
      } catch (e) { 
          console.error("Storage error", e);
          sessionStorage.removeItem('aiResult'); 
      }

      if (!incoming && location.state) {
          incoming = location.state.generatedContent;
          originalRequest = location.state.originalRequest;
      }
      
      if (!incoming) incoming = location.state?.existingCV;

      const aiData = (incoming && incoming.data) ? incoming.data : incoming;

      if (aiData) {
          console.log("📥 Editor Loading Data:", aiData);
          
          setCvData(prev => ({
              ...prev,
              // CRITICAL FIX: Use originalRequest for name/email if available
              fullName: aiData.full_name || originalRequest?.full_name || user?.fullName || prev.fullName,
              email: aiData.email || originalRequest?.email || user?.email || prev.email,
              phone: aiData.phone || prev.phone,
              jobTitle: aiData.desired_job_title || originalRequest?.desired_job_title || prev.jobTitle,
              summary: aiData.professional_summary || prev.summary,
              education: aiData.education_formatted || prev.education,
              experience: Array.isArray(aiData.experience_points) 
                ? '• ' + aiData.experience_points.join('\n• ') 
                : (aiData.experience || ''),
              skills: Array.isArray(aiData.suggested_skills) 
                ? aiData.suggested_skills.join(', ') 
                : (aiData.skills || '')
          }));
          
          if (aiData.id) {
              setCvId(aiData.id);
              if (aiData.template_id) setActiveTemplateId(aiData.template_id);
          }
      } else if (user) {
          setCvData(p => ({...p, fullName: user.fullName || '', email: user.email || ''}));
      }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, location.state]);

  useEffect(() => {
      getTemplates().then(setTemplates).catch(err => console.warn("Template Fetch:", err));
  }, []);

  const handleSave = async (silent=false) => {
      if (!user) {
          alert("⚠️ Session expired. Please log in to save.");
          return null;
      }
      
      // VALIDATION: Check required fields
      if (!cvData.fullName || !cvData.email) {
          alert("⚠️ Name and email are required!");
          return null;
      }
      
      setIsSaving(true);
      try {
          const payload = {
              title: `CV - ${cvData.jobTitle || cvData.fullName || 'New'}`,
              template_id: activeTemplateId,
              data: { 
                  ...cvData,
                  // Ensure all fields are strings, not undefined
                  fullName: cvData.fullName || '',
                  email: cvData.email || '',
                  phone: cvData.phone || '',
                  jobTitle: cvData.jobTitle || '',
                  summary: cvData.summary || '',
                  experience: cvData.experience || '',
                  education: cvData.education || '',
                  skills: cvData.skills || ''
              }
          };
          
          console.log("💾 Saving payload:", payload);
          
          const res = await createCV(payload);
          setCvId(res.id);
          if(!silent) alert(`✅ Saved successfully!`);
          return res.id;
      } catch(e) {
          console.error("Save Error:", e);
          console.error("Error details:", e.response?.data);
          if(!silent) {
              const errorMsg = e.response?.data?.detail || e.message || "Unknown error";
              alert(`❌ Save Failed: ${errorMsg}`);
          }
          return null;
      } finally { 
          setIsSaving(false); 
      }
  };

  if(loading) return <div className="loading-screen">Verifying User...</div>;

  return (
    <div className="App">
      <header className="app-main-header">
        <button onClick={() => navigate('/')} style={{float:'left', padding:'8px'}}>← Back</button>
        <h1>AI CV Editor</h1>
        <div style={{clear:'both', overflowX:'auto'}}>
            <TemplateSelector 
              templates={templates} 
              activeTemplateId={activeTemplateId} 
              setActiveTemplateId={setActiveTemplateId} 
              userIsPremium={user?.subscription_plan === 'pro'} 
            />
        </div>
      </header>
      
      <div className="editor-layout-grid">
        <div className="form-stack">
            <ThemeToolbar data={cvData} setData={setCvData} />
            <CVForm 
              data={cvData} 
              setData={setCvData} 
              customSave={() => handleSave(false)} 
              isSaving={isSaving} 
            />
        </div>
        <div className="preview-stack">
            <CVPreview 
              data={cvData} 
              activeTemplateId={activeTemplateId} 
              cvId={cvId} 
              onAutoSaveRequest={() => handleSave(true)} 
            />
        </div>
      </div>
    </div>
  );
}
export default App;