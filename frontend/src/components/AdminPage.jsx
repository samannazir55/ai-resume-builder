import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/useAuth';
import api from '../services/api';
import './AdminPage.css';

const AdminPage = () => {
  const { user } = useAuth();
  const [tab, setTab] = useState('templates'); // 'templates' or 'packages'
  const [status, setStatus] = useState('');
  
  // -- TEMPLATE STATE --
  const [tmplData, setTmplData] = useState({ id: '', name: '', html_content: '', css_styles: '', is_premium: false, category: 'modern' });
  
  // -- PACKAGE STATE --
  const [packages, setPackages] = useState([]);
  const [pkgData, setPkgData] = useState({ name: '', price: '9.99', credits: 10, description: '', badge: '', payment_link: '' });

  // Load Packages on switch
  useEffect(() => {
    if (tab === 'packages') loadPackages();
  }, [tab]);

  const loadPackages = async () => {
      try {
          const res = await api.get('/admin/packages');
          setPackages(res.data);
      } catch (e) { console.error(e); }
  };

  const handleTemplateSubmit = async (e) => {
    e.preventDefault();
    setStatus('Publishing Template...');
    try {
      await api.post('/admin/templates', tmplData);
      setStatus('✅ Template Published!');
    } catch (err) {
      setStatus('❌ Error: ' + err.message);
    }
  };

  const handlePackageSubmit = async (e) => {
      e.preventDefault();
      try {
          await api.post('/admin/packages', pkgData);
          loadPackages();
          setStatus('✅ Package Live!');
          setPkgData({ name: '', price: '', credits: 10, description: '', badge: '', payment_link: '' });
      } catch (e) { setStatus('❌ ' + e.message); }
  };

  const deletePackage = async (id) => {
      if(!window.confirm("Delete deal?")) return;
      await api.delete(`/admin/packages/${id}`);
      loadPackages();
  };

  if (!user) return <div className="admin-container">Admin Access Only.</div>;

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🛠️ Founder Dashboard</h1>
        <div className="tab-switcher">
            <button className={tab==='templates'?'active':''} onClick={()=>setTab('templates')}>🎨 Templates</button>
            <button className={tab==='packages'?'active':''} onClick={()=>setTab('packages')}>💰 Packages & Pricing</button>
        </div>
        <p className="status-msg">{status}</p>
      </div>

      {tab === 'templates' ? (
          /* TEMPLATE CREATOR FORM */
          <form onSubmit={handleTemplateSubmit} className="admin-grid">
            <div className="admin-sidebar">
              <h3>New Template</h3>
              <div className="form-group"><label>ID</label><input value={tmplData.id} onChange={e=>setTmplData({...tmplData, id:e.target.value})} placeholder="unique_id" /></div>
              <div className="form-group"><label>Name</label><input value={tmplData.name} onChange={e=>setTmplData({...tmplData, name:e.target.value})} /></div>
              <div className="form-group"><label>Category</label><select onChange={e=>setTmplData({...tmplData, category:e.target.value})}><option>modern</option><option>creative</option><option>professional</option></select></div>
              <button type="submit" className="publish-btn">🚀 Publish Design</button>
            </div>
            <div className="admin-code-area">
                <textarea placeholder="HTML (Jinja2)..." value={tmplData.html_content} onChange={e=>setTmplData({...tmplData, html_content:e.target.value})} className="code-input" />
                <textarea placeholder="CSS..." value={tmplData.css_styles} onChange={e=>setTmplData({...tmplData, css_styles:e.target.value})} className="code-input" />
            </div>
          </form>
      ) : (
          /* PACKAGE MANAGER UI */
          <div className="admin-grid">
              <div className="admin-sidebar">
                  <h3>Create Deal</h3>
                  <form onSubmit={handlePackageSubmit}>
                      <div className="form-group"><label>Name</label><input value={pkgData.name} onChange={e=>setPkgData({...pkgData, name:e.target.value})} placeholder="Christmas Deal" /></div>
                      <div className="form-group"><label>Price ($)</label><input type="number" step="0.01" value={pkgData.price} onChange={e=>setPkgData({...pkgData, price:e.target.value})} /></div>
                      <div className="form-group"><label>Credits (Downloads)</label><input type="number" value={pkgData.credits} onChange={e=>setPkgData({...pkgData, credits:e.target.value})} /></div>
                      <div className="form-group"><label>Label</label><input value={pkgData.badge} onChange={e=>setPkgData({...pkgData, badge:e.target.value})} placeholder="HOT / 50% OFF" /></div>
                      <div className="form-group"><label>Payment Link (LemonSqueezy)</label><input value={pkgData.payment_link} onChange={e=>setPkgData({...pkgData, payment_link:e.target.value})} placeholder="https://..." /></div>
                      <button className="publish-btn" style={{background:'#f39c12'}}>💰 Add Package</button>
                  </form>
              </div>
              <div className="packages-list">
                  <h3>Live Packages</h3>
                  {packages.map(p => (
                      <div key={p.id} className="pkg-item">
                          <div><strong>{p.name}</strong> ({p.credits} Credits) - ${p.price}</div>
                          <div><span className="badge">{p.badge}</span> <button onClick={()=>deletePackage(p.id)} className="del-btn">×</button></div>
                      </div>
                  ))}
              </div>
          </div>
      )}
    </div>
  );
};
export default AdminPage;
