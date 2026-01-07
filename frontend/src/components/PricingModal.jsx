import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/useAuth';
import api from '../services/api';
import './PricingModal.css';

const PricingModal = ({ onClose, onSuccess }) => {
  const { user } = useAuth();
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);

  // LOAD PACKAGES FROM ADMIN SETTINGS
  useEffect(() => {
      api.get('/admin/packages').then(res => {
          setPackages(res.data.filter(p => p.is_active));
          setLoading(false);
      }).catch(err => {
          console.error("Failed to load pricing", err);
          setLoading(false);
      });
  }, []);

  const handlePurchase = (pkg) => {
      if (pkg.payment_link) {
          window.open(pkg.payment_link, '_blank');
          // For MVP, assume success for demo flow if needed, 
          // or ideally waiting for webhook (out of scope for today)
          // user clicks 'I have paid' button logic could go here
      } else {
          alert("Payment link not configured for this package yet.");
      }
  };

  return (
    <div className="pricing-overlay">
      <div className="pricing-content">
        <button className="close-btn" onClick={onClose}>×</button>
        <div className="pricing-header">
            <h2>🛒 Resume Store</h2>
            <p>Your Balance: <span style={{color:'#667eea', fontWeight:'bold'}}>{user?.credits || 0} Credits</span></p>
        </div>

        {loading ? <div style={{textAlign:'center'}}>Loading Deals...</div> : (
            <div className="pricing-grid">
                {packages.map(pkg => (
                    <div key={pkg.id} className="price-card pro">
                        {pkg.badge && <div className="tag popular">{pkg.badge}</div>}
                        <h3>${pkg.price}</h3>
                        <div className="credits-display">{pkg.credits} Credits</div>
                        <p style={{fontSize:'13px', color:'#666'}}>{pkg.description}</p>
                        
                        <button className="plan-btn fill" onClick={() => handlePurchase(pkg)}>
                            Buy Now
                        </button>
                    </div>
                ))}
            </div>
        )}
      </div>
    </div>
  );
};
export default PricingModal;
