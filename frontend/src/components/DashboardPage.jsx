import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import { getCVs, deleteCV } from '../services/api';
import './DashboardPage.css';

const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [cvs, setCvs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load documents on mount
  useEffect(() => {
    fetchDocuments();
  }, [user]);

  const fetchDocuments = async () => {
    if (!user) return;
    try {
      const data = await getCVs();
      // Sort newest first
      const sorted = data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setCvs(sorted);
    } catch (err) {
      console.error(err);
      setError("Could not load your documents.");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (cv) => {
    // 🔥 CRITICAL FIX: Pass template_id via forceTemplate
    console.log("✏️ Editing CV:", cv.id, "Template:", cv.template_id);
    navigate('/editor', { 
      state: { 
        existingCV: cv,
        forceTemplate: cv.template_id  // ← THIS WAS MISSING!
      } 
    });
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this resume? This cannot be undone.")) {
      try {
        await deleteCV(id);
        setCvs(prev => prev.filter(c => c.id !== id));
      } catch (err) {
        alert("Failed to delete. " + err.message);
      }
    }
  };

  const handleNew = () => {
    navigate('/'); // Go to Chat
  };

  if (loading) return <div className="dash-loading">Loading your workspace...</div>;

  return (
    <div className="dashboard-container">
      {/* SIDEBAR NAVIGATION (Simple) */}
      <aside className="dash-sidebar">
        <div className="user-profile">
            <div className="avatar-circle">{user?.fullName?.charAt(0) || 'U'}</div>
            <div className="user-details">
                <h3>{user?.fullName}</h3>
                <span>{user?.subscription_plan || 'Free Plan'}</span>
            </div>
        </div>
        
        <nav className="dash-nav">
            <button className="nav-item active">📂 My Documents</button>
            <button className="nav-item">💳 Billing (Coming Soon)</button>
            <button className="nav-item logout" onClick={() => window.location.href='/login'}>Sign Out</button>
        </nav>
      </aside>

      {/* MAIN CONTENT */}
      <main className="dash-content">
        <div className="dash-header">
            <h1>My Documents</h1>
            <button className="create-new-btn" onClick={handleNew}>+ Create New Resume</button>
        </div>

        {error && <div className="error-banner">{error}</div>}

        {cvs.length === 0 ? (
            <div className="empty-state">
                <div className="empty-icon">📄</div>
                <h3>No resumes yet!</h3>
                <p>Start a chat with our AI to build your first professional CV.</p>
                <button onClick={handleNew}>Get Started</button>
            </div>
        ) : (
            <div className="cv-grid">
                {cvs.map(cv => (
                    <div key={cv.id} className="cv-card">
                        <div className="cv-preview-placeholder">
                            {/* Enhanced template badge with proper capitalization */}
                            <span className="template-badge">
                              {cv.template_id 
                                ? cv.template_id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
                                : 'Modern'}
                            </span>
                            <div className="paper-look"></div>
                        </div>
                        <div className="cv-info">
                            <h4>{cv.title || 'Untitled Resume'}</h4>
                            <small>Edited: {new Date(cv.updated_at || Date.now()).toLocaleDateString()}</small>
                            <div className="cv-actions">
                                <button className="btn-edit" onClick={() => handleEdit(cv)}>✏️ Edit</button>
                                <button className="btn-del" onClick={() => handleDelete(cv.id)}>🗑️</button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        )}
      </main>
    </div>
  );
};

export default DashboardPage;