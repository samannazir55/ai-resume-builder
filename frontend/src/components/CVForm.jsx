import React, { useRef } from 'react';

const CVForm = ({ data, setData, customSave, isSaving }) => {
  const fileInputRef = useRef(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => setData(p => ({ ...p, profileImage: ev.target.result }));
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="cv-form-container">
      <h2>✏️ Edit Details</h2>
      
      {/* Profile Image Upload */}
      <div className="form-group image-upload-group">
          <div onClick={() => fileInputRef.current.click()} style={{cursor:'pointer', textAlign:'center', marginBottom:'10px'}}>
             {data.profileImage ? (
                 <img src={data.profileImage} alt="Profile" style={{width:80, height:80, borderRadius:'50%', objectFit:'cover'}} />
             ) : (
                 <div style={{width:80, height:80, background:'#eee', borderRadius:'50%', margin:'0 auto', lineHeight:'80px'}}>📷</div>
             )}
          </div>
          <input ref={fileInputRef} type="file" hidden accept="image/*" onChange={handleImageUpload} />
      </div>

      {/* Basic Information */}
      <h3 style={{marginTop:'20px', color:'#2c3e50', borderBottom:'2px solid #eee', paddingBottom:'8px'}}>📋 Basic Info</h3>
      {['fullName', 'email', 'phone', 'jobTitle'].map(f => (
          <div className="form-group" key={f}>
            <label style={{textTransform:'capitalize', fontWeight:'600'}}>
              {f.replace(/([A-Z])/g, ' $1')}
            </label>
            <input name={f} value={data[f]||''} onChange={handleChange} />
          </div>
      ))}

      {/* NEW: Location Field */}
      <div className="form-group">
        <label style={{fontWeight:'600'}}>📍 Location</label>
        <input 
          name="location" 
          value={data.location||''} 
          onChange={handleChange}
          placeholder="e.g., Rawalpindi, Pakistan" 
        />
      </div>

      {/* Main Content Sections */}
      <h3 style={{marginTop:'20px', color:'#2c3e50', borderBottom:'2px solid #eee', paddingBottom:'8px'}}>📝 Main Content</h3>
      
      <div className="form-group">
        <label style={{fontWeight:'600'}}>Professional Summary</label>
        <textarea name="summary" value={data.summary||''} onChange={handleChange} rows={4} />
      </div>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>Experience</label>
        <textarea name="experience" value={data.experience||''} onChange={handleChange} rows={6} 
          placeholder="• Your first experience point&#10;• Your second experience point" />
      </div>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>Education</label>
        <textarea name="education" value={data.education||''} onChange={handleChange} rows={4} />
      </div>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>Skills (comma-separated)</label>
        <textarea name="skills" value={data.skills||''} onChange={handleChange} rows={2}
          placeholder="Python, JavaScript, React, FastAPI" />
      </div>

      {/* NEW: Custom Sidebar Fields */}
      <h3 style={{marginTop:'20px', color:'#2c3e50', borderBottom:'2px solid #eee', paddingBottom:'8px'}}>
        🎨 Custom Sidebar Content
      </h3>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>🎯 Hobbies/Interests (comma-separated)</label>
        <input 
          name="hobbies" 
          value={data.hobbies||''} 
          onChange={handleChange}
          placeholder="Reading, Photography, Hiking, Gaming" 
        />
      </div>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>🌐 Languages (comma-separated)</label>
        <input 
          name="languages" 
          value={data.languages||''} 
          onChange={handleChange}
          placeholder="English (Native), Urdu (Fluent), Arabic (Basic)" 
        />
      </div>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>🏆 Certifications (comma-separated)</label>
        <input 
          name="certifications" 
          value={data.certifications||''} 
          onChange={handleChange}
          placeholder="AWS Certified, PMP, Google Analytics" 
        />
      </div>

      {/* NEW: Social Links */}
      <h3 style={{marginTop:'20px', color:'#2c3e50', borderBottom:'2px solid #eee', paddingBottom:'8px'}}>
        🔗 Social Links
      </h3>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>LinkedIn</label>
        <input 
          name="linkedin" 
          value={data.linkedin||''} 
          onChange={handleChange}
          placeholder="https://linkedin.com/in/yourprofile" 
        />
      </div>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>GitHub</label>
        <input 
          name="github" 
          value={data.github||''} 
          onChange={handleChange}
          placeholder="https://github.com/yourusername" 
        />
      </div>

      <div className="form-group">
        <label style={{fontWeight:'600'}}>Portfolio</label>
        <input 
          name="portfolio" 
          value={data.portfolio||''} 
          onChange={handleChange}
          placeholder="https://yourportfolio.com" 
        />
      </div>

      {/* Save Button */}
      <button 
        type="button" 
        onClick={customSave} 
        className="submit-button"
        disabled={isSaving}
        style={{marginTop:'20px', width:'100%', padding:'12px', fontSize:'16px'}}
      >
        {isSaving ? "Saving..." : "💾 Update Preview / Save"}
      </button>
    </div>
  );
};

export default CVForm;