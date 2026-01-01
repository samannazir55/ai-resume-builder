import React, { useState } from 'react';
import { useAuth } from '../context/useAuth';
import api from '../services/api';
import './AdminPage.css';

const AdminPage = () => {
  const { user } = useAuth();
  
  // State for the new template
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    html_content: '',
    css_styles: '',
    is_premium: false,
    category: 'modern'
  });
  const [status, setStatus] = useState('');

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Publishing...');
    try {
      await api.post('/admin/templates', formData);
      setStatus('✅ Published Successfully! It is now Live.');
    } catch (err) {
      setStatus(`❌ Error: ${err.response?.data?.detail || err.message}`);
    }
  };

  if (!user) return <div className="admin-container">Please Login.</div>;

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>🛠️ Template Factory</h1>
        <p>Paste your ChatGPT code here to launch a new design instantly.</p>
      </div>

      <form onSubmit={handleSubmit} className="admin-grid">
        <div className="admin-sidebar">
          <div className="form-group">
             <label>Template ID (unique)</label>
             <input name="id" value={formData.id} onChange={handleChange} placeholder="creative_orange" required />
          </div>
          <div className="form-group">
             <label>Display Name</label>
             <input name="name" value={formData.name} onChange={handleChange} placeholder="Creative Orange" required />
          </div>
          <div className="form-group">
             <label>Category</label>
             <select name="category" value={formData.category} onChange={handleChange}>
                 <option value="modern">Modern</option>
                 <option value="professional">Professional</option>
                 <option value="creative">Creative</option>
             </select>
          </div>
          <div className="form-group checkbox-group">
             <label>
               <input type="checkbox" name="is_premium" checked={formData.is_premium} onChange={handleChange} />
               Is Premium? 💎
             </label>
          </div>
          <button type="submit" className="publish-btn">🚀 Publish Live</button>
          <div className="status-msg">{status}</div>
        </div>

        <div className="admin-code-area">
          <div className="code-box">
             <label>HTML (Jinja2 Format)</label>
             <textarea name="html_content" value={formData.html_content} onChange={handleChange} placeholder="<div class='resume'>...</div>" required />
          </div>
          <div className="code-box">
             <label>CSS</label>
             <textarea name="css_styles" value={formData.css_styles} onChange={handleChange} placeholder=".resume { ... }" required />
          </div>
        </div>
      </form>
    </div>
  );
};

export default AdminPage;
