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
      <h2>Edit Details</h2>
      <div className="form-group image-upload-group">
          <div onClick={() => fileInputRef.current.click()} style={{cursor:'pointer', textAlign:'center', marginBottom:'10px'}}>
             {data.profileImage ? (
                 <img src={data.profileImage} style={{width:80, height:80, borderRadius:'50%', objectFit:'cover'}} />
             ) : (
                 <div style={{width:80, height:80, background:'#eee', borderRadius:'50%', margin:'0 auto', lineHeight:'80px'}}>📷</div>
             )}
          </div>
          <input ref={fileInputRef} type="file" hidden accept="image/*" onChange={handleImageUpload} />
      </div>

      {['fullName', 'email', 'phone', 'jobTitle'].map(f => (
          <div className="form-group" key={f}>
            <label style={{textTransform:'capitalize'}}>{f.replace(/([A-Z])/g, ' $1')}</label>
            <input name={f} value={data[f]||''} onChange={handleChange} />
          </div>
      ))}
      
      {['summary', 'experience', 'education', 'skills'].map(f => (
          <div className="form-group" key={f}>
            <label style={{textTransform:'capitalize'}}>{f}</label>
            <textarea name={f} value={data[f]||''} onChange={handleChange} rows={f === 'skills' ? 2 : 5} />
          </div>
      ))}

      {/* Replaced Submit Button with Trigger */}
      <button 
        type="button" 
        onClick={customSave} 
        className="submit-button"
        disabled={isSaving}
      >
        {isSaving ? "Saving..." : "💾 Update Preview / Save"}
      </button>
    </div>
  );
};
export default CVForm;
