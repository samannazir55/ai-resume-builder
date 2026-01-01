import React, { useState } from 'react';
import { useAuth } from '../context/useAuth';
import './PricingModal.css';

const PricingModal = ({ onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  const handlePurchase = (plan) => {
    setLoading(true);
    // SIMULATE STRIPE DELAY
    setTimeout(() => {
        setLoading(false);
        alert(`🎉 Payment Successful! You are now on the ${plan} Plan.`);
        onSuccess(); // Trigger the unlock
        onClose();   // Close modal
    }, 2000);
  };

  return (
    <div className="pricing-overlay">
      <div className="pricing-content">
        <button className="close-btn" onClick={onClose}>×</button>
        
        <div className="pricing-header">
            <h2>🚀 Unlock Your Career Potential</h2>
            <p>Select a plan to access Premium Templates and Advanced AI.</p>
        </div>

        <div className="pricing-grid">
            {/* FREE TIER */}
            <div className="price-card basic">
                <div className="tag">STARTER</div>
                <h3>Free</h3>
                <div className="price">$0<span>/mo</span></div>
                <ul>
                    <li>✅ 3 Basic Templates</li>
                    <li>✅ Standard PDF Export</li>
                    <li>❌ Manual Watermark</li>
                    <li>❌ AI Improvements</li>
                </ul>
                <button className="plan-btn outline" disabled>Current Plan</button>
            </div>

            {/* PRO TIER */}
            <div className="price-card pro">
                <div className="tag popular">MOST POPULAR</div>
                <h3>Pro Access</h3>
                <div className="price">$9.99<span>/mo</span></div>
                <ul>
                    <li>💎 <b>Access 50+ Premium Templates</b></li>
                    <li>🧠 Unlimited AI Re-Writes</li>
                    <li>📄 No Watermarks</li>
                    <li>🚀 Priority Support</li>
                </ul>
                <button 
                    className="plan-btn fill" 
                    onClick={() => handlePurchase('PRO')}
                    disabled={loading}
                >
                    {loading ? "Processing..." : "Upgrade Now"}
                </button>
            </div>
        </div>
        
        <p className="guarantee">🔒 Secure payment powered by Stripe. Cancel anytime.</p>
      </div>
    </div>
  );
};

export default PricingModal;
