import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, error } = useAuth();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    const result = await login(email, password);
    if (result.success) {
      navigate('/dashboard'); // Go to dashboard if logged in
    }
    setIsSubmitting(false);
  };

  return (
    <div className="auth-page" style={{display:'flex',justifyContent:'center', alignItems:'center', height:'100vh', background:'#f8fafc'}}>
      <div className="auth-form-container" style={{background:'white', padding:'40px', borderRadius:'12px', boxShadow:'0 4px 12px rgba(0,0,0,0.1)', width:'400px'}}>
        <h2 style={{textAlign:'center', marginBottom:'20px', color:'#2c3e50'}}>Welcome Back</h2>
        
        {error && <div style={{background:'#fee2e2', color:'#dc2626', padding:'10px', borderRadius:'6px', marginBottom:'20px', fontSize:'14px'}}>{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{marginBottom:'15px'}}>
            <label style={{display:'block', marginBottom:'5px', fontSize:'14px', fontWeight:'600'}}>Email</label>
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} required style={{width:'100%', padding:'10px', borderRadius:'6px', border:'1px solid #ddd'}} />
          </div>
          <div className="form-group" style={{marginBottom:'25px'}}>
            <label style={{display:'block', marginBottom:'5px', fontSize:'14px', fontWeight:'600'}}>Password</label>
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} required style={{width:'100%', padding:'10px', borderRadius:'6px', border:'1px solid #ddd'}} />
          </div>
          <button type="submit" className="submit-button" disabled={isSubmitting} style={{width:'100%', padding:'12px', background:'#667eea', color:'white', border:'none', borderRadius:'6px', cursor:'pointer', fontWeight:'bold'}}>
            {isSubmitting ? 'Logging in...' : 'Log In'}
          </button>
        </form>
        
        <p style={{textAlign:'center', marginTop:'20px', fontSize:'14px'}}>
          Need an account? <Link to="/register" style={{color:'#667eea', fontWeight:'bold'}}>Register</Link>
        </p>
      </div>
    </div>
  );
};
export default LoginPage;
