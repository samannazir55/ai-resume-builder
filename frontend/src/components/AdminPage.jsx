import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/useAuth';
import api from '../services/api';
import './AdminPage.css';

const AdminPage = () => {
  const { user } = useAuth();

  /* =========================
     UI STATE
  ========================= */
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [status, setStatus] = useState({ message: '', type: '' });

  /* =========================
     PACKAGE STATE
  ========================= */
  const [packages, setPackages] = useState([]);
  const [showPackageModal, setShowPackageModal] = useState(false);
  const [editingPackage, setEditingPackage] = useState(null);
  const [regionalLinks, setRegionalLinks] = useState([]);

  const [packageForm, setPackageForm] = useState({
    name: '',
    price_usd: '',
    credits: 10,
    description: '',
    stripe_payment_link: '',
    lemonsqueezy_link: '',
    paddle_product_id: '',
    regional_payment_links: {},
    badge: '',
    is_active: true
  });

  /* =========================
     TEMPLATE STATE
  ========================= */
  const [templates, setTemplates] = useState([]);
  const [showTemplateModal, setShowTemplateModal] = useState(false);

  const [templateForm, setTemplateForm] = useState({
    id: '',
    name: '',
    category: 'professional',
    is_premium: false,
    html_content: '',
    css_styles: ''
  });

  /* =========================
     UTILITIES
  ========================= */
  const showStatus = (message, type) => {
    setStatus({ message, type });
    setTimeout(() => setStatus({ message: '', type: '' }), 5000);
  };

  const getBadgeClass = (badge) => {
    if (!badge) return 'badge-default';
    const b = badge.toLowerCase();
    if (b.includes('popular')) return 'badge-popular';
    if (b.includes('hot')) return 'badge-hot';
    if (b.includes('new')) return 'badge-new';
    return 'badge-default';
  };

  /* =========================
     API — PACKAGES
  ========================= */
  const loadPackages = useCallback(async () => {
    try {
      const res = await api.get('/admin/packages');
      setPackages(res.data);
    } catch {
      showStatus('Failed to load packages', 'error');
    }
  }, []);

  const savePackage = async (e) => {
    e.preventDefault();

    const regionalObj = {};
    regionalLinks.forEach((r) => {
      regionalObj[r.code] = {
        name: r.name,
        link: r.link,
        instructions: r.instructions
      };
    });

    try {
      const payload = {
        ...packageForm,
        regional_payment_links: JSON.stringify(regionalObj)
      };

      if (editingPackage) {
        await api.put(`/admin/packages/${editingPackage.id}`, payload);
        showStatus('✅ Package updated', 'success');
      } else {
        await api.post('/admin/packages', payload);
        showStatus('✅ Package created', 'success');
      }

      setShowPackageModal(false);
      resetPackageForm();
      loadPackages();
    } catch (err) {
      showStatus(err.message || 'Error saving package', 'error');
    }
  };

  const resetPackageForm = () => {
    setPackageForm({
      name: '',
      price_usd: '',
      credits: 10,
      description: '',
      stripe_payment_link: '',
      lemonsqueezy_link: '',
      paddle_product_id: '',
      regional_payment_links: {},
      badge: '',
      is_active: true
    });
    setRegionalLinks([]);
    setEditingPackage(null);
  };

  const openEditPackage = (pkg) => {
    setEditingPackage(pkg);
    setPackageForm(pkg);

    if (pkg.regional_payment_links) {
      try {
        const parsed = JSON.parse(pkg.regional_payment_links);
        setRegionalLinks(
          Object.entries(parsed).map(([code, data]) => ({
            code,
            ...data
          }))
        );
      } catch {
        setRegionalLinks([]);
      }
    }
    setShowPackageModal(true);
  };

  const removeRegionalLink = (idx) => {
    setRegionalLinks(regionalLinks.filter((_, i) => i !== idx));
  };

  /* =========================
     API — TEMPLATES
  ========================= */
  const loadTemplates = useCallback(async () => {
    try {
      const res = await api.get('/templates');
      setTemplates(res.data);
    } catch {
      showStatus('Failed to load templates', 'error');
    }
  }, []);

  const saveTemplate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/templates', templateForm);
      showStatus('✅ Template saved', 'success');
      setShowTemplateModal(false);
      resetTemplateForm();
      loadTemplates();
    } catch (err) {
      showStatus(err.message || 'Template save failed', 'error');
    }
  };

  const resetTemplateForm = () => {
    setTemplateForm({
      id: '',
      name: '',
      category: 'professional',
      is_premium: false,
      html_content: '',
      css_styles: ''
    });
  };

  /* =========================
     EFFECTS
  ========================= */
  useEffect(() => {
    if (activeTab === 'packages') loadPackages();
    if (activeTab === 'templates') loadTemplates();
  }, [activeTab]); // Removed loadPackages and loadTemplates from dependencies

  /* =========================
     AUTH GUARD
  ========================= */
  if (!user) {
    return (
      <div className="cms-container">
        <div className="cms-main center">
          <h1>🔒 Admin Access Required</h1>
        </div>
      </div>
    );
  }

  /* =========================
     RENDER TAB CONTENT
  ========================= */
  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div>
            <h1>📊 Dashboard</h1>
            <div className="dashboard-stats">
              <div className="stat-card">
                <h3>Total Packages</h3>
                <p className="stat-number">{packages.length}</p>
              </div>
              <div className="stat-card">
                <h3>Total Templates</h3>
                <p className="stat-number">{templates.length}</p>
              </div>
              <div className="stat-card">
                <h3>Active Packages</h3>
                <p className="stat-number">
                  {packages.filter(p => p.is_active).length}
                </p>
              </div>
            </div>
          </div>
        );

      case 'packages':
        return (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h1>📦 Packages</h1>
              <button
                className="btn-primary"
                onClick={() => setShowPackageModal(true)}
              >
                ➕ New Package
              </button>
            </div>
            <div className="packages-list">
              {packages.map((pkg) => (
                <div key={pkg.id} className="package-card">
                  <h3>{pkg.name}</h3>
                  <p>${pkg.price_usd} - {pkg.credits} credits</p>
                  <p>{pkg.description}</p>
                  {pkg.badge && (
                    <span className={getBadgeClass(pkg.badge)}>{pkg.badge}</span>
                  )}
                  <button onClick={() => openEditPackage(pkg)}>Edit</button>
                </div>
              ))}
            </div>
          </div>
        );

      case 'templates':
        return (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h1>🎨 Templates</h1>
              <button
                className="btn-primary"
                onClick={() => setShowTemplateModal(true)}
              >
                ➕ New Template
              </button>
            </div>
            <div className="templates-list">
              {templates.map((tmpl) => (
                <div key={tmpl.id} className="template-card">
                  <h3>{tmpl.name}</h3>
                  <p>Category: {tmpl.category}</p>
                  <p>{tmpl.is_premium ? '⭐ Premium' : '🆓 Free'}</p>
                </div>
              ))}
            </div>
          </div>
        );

      case 'settings':
        return (
          <div>
            <h1>⚙️ Settings</h1>
            <p>Settings panel coming soon...</p>
          </div>
        );

      default:
        return <div>Select a tab</div>;
    }
  };

  /* =========================
     MAIN RENDER
  ========================= */
  return (
    <div className="cms-container">
      <button
        className="cms-mobile-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        ☰
      </button>

      <div className={`cms-sidebar ${sidebarOpen ? 'mobile-open' : ''}`}>
        <h2>🛠️ Admin CMS</h2>
        <nav>
          {['dashboard', 'packages', 'templates', 'settings'].map((tab) => (
            <div
              key={tab}
              className={`cms-nav-item ${
                activeTab === tab ? 'active' : ''
              }`}
              onClick={() => {
                setActiveTab(tab);
                setSidebarOpen(false);
              }}
            >
              {tab}
              {tab === 'packages' && (
                <span className="pkg-count"> ({packages.length})</span>
              )}
            </div>
          ))}
        </nav>
        <div className="cms-sidebar-footer">Logged in as {user.email}</div>
      </div>

      <div className="cms-main">
        {status.message && (
          <div className={`status-message ${status.type}`}>
            {status.message}
          </div>
        )}
        
        {renderTabContent()}
      </div>

      {/* ================= PACKAGE MODAL ================= */}
      {showPackageModal && (
        <div
          className="modal-overlay"
          onClick={() => setShowPackageModal(false)}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <form onSubmit={savePackage}>
              <h2>
                {editingPackage ? '✏️ Edit Package' : '➕ Create Package'}
              </h2>

              {regionalLinks.map((region, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start'
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <strong>
                      {region.code} - {region.name}
                    </strong>
                    {region.link && <div>Link: {region.link}</div>}
                    {region.instructions && (
                      <div style={{ whiteSpace: 'pre-line' }}>
                        {region.instructions}
                      </div>
                    )}
                  </div>

                  <button
                    type="button"
                    className="btn-danger"
                    onClick={() => removeRegionalLink(idx)}
                  >
                    Remove
                  </button>
                </div>
              ))}

              <div className="modal-footer">
                <button
                  type="button"
                  onClick={() => setShowPackageModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= TEMPLATE MODAL ================= */}
      {showTemplateModal && (
        <div
          className="modal-overlay"
          onClick={() => setShowTemplateModal(false)}
        >
          <div
            className="modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <form onSubmit={saveTemplate}>
              <h2>➕ Create Template</h2>
              
              <div className="modal-footer">
                <button
                  type="button"
                  onClick={() => setShowTemplateModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage;