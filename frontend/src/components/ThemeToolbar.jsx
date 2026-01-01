import React from 'react';

const ThemeToolbar = ({ data, setData }) => {
  const colors = ["#2c3e50", "#c0392b", "#27ae60", "#8e44ad", "#d35400", "#000000"];

  const fonts = [
    { name: "System Standard", value: "Helvetica, Arial, sans-serif" },
    { name: "Roboto (Clean)", value: "'Roboto', sans-serif" },
    { name: "Open Sans (Neutral)", value: "'Open Sans', sans-serif" },
    { name: "Lato (Friendly)", value: "'Lato', sans-serif" },
    { name: "Montserrat (Modern)", value: "'Montserrat', sans-serif" },
    { name: "Raleway (Elegant)", value: "'Raleway', sans-serif" },
    { name: "Oswald (Bold)", value: "'Oswald', sans-serif" },
    { name: "Playfair Display (Luxury)", value: "'Playfair Display', serif" },
    { name: "Lora (Print Look)", value: "'Lora', serif" },
    { name: "Merriweather (Readability)", value: "'Merriweather', serif" },
    { name: "Roboto Slab (Technical)", value: "'Roboto Slab', serif" }
  ];

  const update = (field, value) => {
    setData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div style={{
      background: 'white', padding: '15px', borderRadius: '8px', 
      marginBottom: '20px', border: '1px solid #ddd', boxShadow: '0 2px 5px rgba(0,0,0,0.05)'
    }}>
      <h3 style={{marginTop:0, fontSize:'13px', textTransform:'uppercase', borderBottom:'1px solid #eee', paddingBottom:'10px'}}>🎨 Design Studio</h3>
      
      {/* 1. FONT SELECTION */}
      <div style={{marginBottom: '15px'}}>
        <label style={{fontSize:'12px', fontWeight:'bold', display:'block', marginBottom:'5px', color:'#666'}}>Typography</label>
        <select 
            onChange={(e) => update('fontFamily', e.target.value)}
            value={data.fontFamily}
            style={{width: '100%', padding:'8px', borderRadius:'4px', border:'1px solid #ccc', fontFamily: 'inherit'}}
        >
            {fonts.map(f => (
                <option key={f.name} value={f.value}>{f.name}</option>
            ))}
        </select>
      </div>

      <div style={{display:'flex', gap:'20px'}}>
          {/* 2. ACCENT COLOR */}
          <div style={{flex:1}}>
            <label style={{fontSize:'12px', fontWeight:'bold', display:'block', marginBottom:'5px', color:'#666'}}>Theme Color</label>
            <div style={{display:'flex', gap:'5px', alignItems:'center'}}>
                <input 
                    type="color" 
                    value={data.accentColor || '#2c3e50'} 
                    onChange={(e) => update('accentColor', e.target.value)}
                    style={{width:'100%', height:'35px', padding:0, border:'none', borderRadius:'4px', cursor:'pointer'}}
                />
            </div>
          </div>

          {/* 3. TEXT COLOR */}
          <div style={{flex:1}}>
            <label style={{fontSize:'12px', fontWeight:'bold', display:'block', marginBottom:'5px', color:'#666'}}>Text Color</label>
            <div style={{display:'flex', gap:'5px', alignItems:'center'}}>
                <input 
                    type="color" 
                    value={data.textColor || '#333333'} 
                    onChange={(e) => update('textColor', e.target.value)}
                    style={{width:'100%', height:'35px', padding:0, border:'none', borderRadius:'4px', cursor:'pointer'}}
                />
            </div>
          </div>
      </div>
      
      {/* QUICK PRESETS */}
      <div style={{marginTop: '10px', display: 'flex', gap: '5px', flexWrap:'wrap'}}>
        {colors.map(c => (
            <div key={c} onClick={() => update('accentColor', c)} 
                 style={{width:'20px', height:'20px', background:c, borderRadius:'50%', cursor:'pointer', border:'1px solid #ddd'}} />
        ))}
      </div>

    </div>
  );
};

export default ThemeToolbar;
