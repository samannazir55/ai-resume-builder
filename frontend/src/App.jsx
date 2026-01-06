import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './context/useAuth';
import api, { getTemplates, createCV, updateCV } from './services/api';
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
    location: '', hobbies: '', languages: '', certifications: '',
    linkedin: '', github: '', portfolio: '',
    accentColor: '#2c3e50', textColor: '#333333', fontFamily: 'Helvetica, Arial, sans-serif'
  });
  
  const [templates, setTemplates] = useState([]); 
  const [activeTemplateId, setActiveTemplateId] = useState('modern');
  const [cvId, setCvId] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // Track which location key we've processed to prevent re-processing
  const processedLocationKey = useRef(null);

  // 1. LOAD TEMPLATES
  useEffect(() => {
    getTemplates()
      .then(data => {
        setTemplates(data);
        console.log('✅ Templates loaded:', data.length);
      })
      .catch(err => console.error('❌ Template load error:', err));
  }, []);

  // 2. PROCESS NAVIGATION STATE - FIXED VERSION
  useEffect(() => {
    // Only process if this is a new navigation (different location.key)
    if (processedLocationKey.current === location.key) {
      return;
    }

    console.log('🔄 Processing navigation state...', location.key);
    
    // Try to get incoming data from multiple sources
    let incomingData = null;
    let forceTemplate = null;
    
    // Priority 1: Check for forced template (from Dashboard or Store)
    if (location.state?.forceTemplate) {
      forceTemplate = location.state.forceTemplate;
      console.log('💎 FORCE TEMPLATE detected:', forceTemplate);
    }
    
    // Priority 2: Check for existing CV data
    if (location.state?.existingCV) {
      incomingData = location.state.existingCV;
      console.log('📋 Existing CV detected:', incomingData.id);
    } 
    // Priority 3: Check for AI-generated content
    else if (location.state?.generatedContent) {
      incomingData = location.state.generatedContent;
      console.log('🤖 AI generated content detected');
    }
    // Priority 4: Check session storage
    else {
      try {
        const sessionData = sessionStorage.getItem('aiResult');
        if (sessionData && sessionData !== 'undefined') {
          incomingData = JSON.parse(sessionData);
          console.log('💾 Session storage data detected');
          sessionStorage.removeItem('aiResult'); // Clean up
        }
      } catch (e) {
        console.error('Session storage parse error:', e);
        sessionStorage.removeItem('aiResult');
      }
    }

    // PROCESS THE DATA
    if (incomingData) {
      const cvRecord = incomingData.data ? incomingData : { data: incomingData };
      const dataObj = cvRecord.data || cvRecord;
      
      console.log('📥 Loading CV data:', {
        id: cvRecord.id,
        template: cvRecord.template_id,
        hasData: !!dataObj
      });

      // Helper functions
      const processExp = (val) => 
        Array.isArray(val) ? val.map(p => `• ${p}`).join('\n') : (val || '');
      const processSkill = (val) => 
        Array.isArray(val) ? val.join(', ') : (val || '');

      // Update CV data
      setCvData(prev => ({
        ...prev,
        fullName: dataObj.fullName || dataObj.full_name || user?.fullName || prev.fullName,
        email: dataObj.email || user?.email || prev.email,
        phone: dataObj.phone || prev.phone,
        jobTitle: dataObj.jobTitle || dataObj.desired_job_title || prev.jobTitle,
        summary: dataObj.summary || dataObj.professional_summary || prev.summary,
        education: dataObj.education || dataObj.education_formatted || prev.education,
        experience: processExp(dataObj.experience || dataObj.experience_points),
        skills: processSkill(dataObj.skills || dataObj.suggested_skills),
        location: dataObj.location || prev.location,
        hobbies: dataObj.hobbies || prev.hobbies,
        languages: dataObj.languages || prev.languages,
        certifications: dataObj.certifications || prev.certifications,
        linkedin: dataObj.linkedin || prev.linkedin,
        github: dataObj.github || prev.github,
        portfolio: dataObj.portfolio || prev.portfolio,
        accentColor: dataObj.accentColor || prev.accentColor,
        textColor: dataObj.textColor || prev.textColor,
        fontFamily: dataObj.fontFamily || prev.fontFamily
      }));
      
      // Set CV ID if available
      if (cvRecord.id) {
        console.log('🆔 Setting CV ID:', cvRecord.id);
        setCvId(cvRecord.id);
      }
      
      // Set template - prioritize forced template, then CV's template
      const templateToUse = forceTemplate || cvRecord.template_id || 'modern';
      console.log('🎨 Setting template:', templateToUse);
      setActiveTemplateId(templateToUse);
      
    } else if (forceTemplate) {
      // Just a template change without data (shouldn't happen, but handle it)
      console.log('🎨 Template change only:', forceTemplate);
      setActiveTemplateId(forceTemplate);
    } else if (user && !cvData.fullName) {
      // No incoming data, populate with user defaults
      console.log('👤 Using user defaults');
      setCvData(prev => ({
        ...prev,
        fullName: user.fullName || '',
        email: user.email || ''
      }));
    }

    // Mark this location as processed
    processedLocationKey.current = location.key;
    
    // Clean up navigation state after processing
    if (location.state) {
      navigate(location.pathname, { replace: true, state: {} });
    }
    
  }, [location.state, location.key, user]); // Added location.key to dependencies

  const handleSave = async (silent = false) => {
    if (!user) {
      if (!silent) alert("Please log in to save.");
      return null;
    }
    
    setIsSaving(true);
    try {
      const payload = {
        title: `Resume - ${cvData.jobTitle || cvData.fullName || 'New'}`,
        template_id: activeTemplateId,
        data: { ...cvData }
      };
      
      let res;
      if (cvId) {
        // Update existing CV
        res = await updateCV(cvId, payload);
        console.log('✅ CV updated:', cvId);
      } else {
        // Create new CV
        res = await createCV(payload);
        setCvId(res.id);
        console.log('✅ CV created:', res.id);
      }
      
      if (!silent) alert(`✅ CV Saved! ID: ${res.id}`);
      setIsSaving(false);
      return res.id;
    } catch (err) {
      console.error('❌ Save error:', err);
      if (!silent) alert("Save failed: " + (err.message || 'Unknown error'));
      setIsSaving(false);
      return null;
    }
  };

  if (loading) return <div className="loading-screen">Loading...</div>;

  return (
    <div className="App">
      <header className="app-main-header">
        <div style={{display:'flex', alignItems:'center', justifyContent:'center', position:'relative'}}>
          <button onClick={() => window.location.href='/dashboard'} className="back-dash-btn">
            ⬅️ Dashboard
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