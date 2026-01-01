import { createContext, useContext, useState, useEffect } from 'react';
// Verify imports are standard
import { login as apiLogin, register as apiRegister, getProfile } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 1. Initialize User on Load
  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const u = await getProfile();
          // Map backend snake_case to frontend keys
          setUser({
              ...u,
              fullName: u.full_name,
              subscription_plan: u.subscription_plan
          });
        } catch (e) {
          console.error("Auth Load Error", e);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  // 2. Login Wrapper
  const login = async (email, password) => {
    try {
      setError(null);
      await apiLogin(email, password);
      
      const u = await getProfile();
      setUser({
          ...u,
          fullName: u.full_name,
          subscription_plan: u.subscription_plan
      });
      return { success: true };
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.detail || "Login failed.";
      setError(msg);
      return { success: false, error: msg };
    }
  };

  // 3. Register Wrapper
  const register = async (name, email, password) => {
    try {
      setError(null);
      // Construct backend object here
      await apiRegister({ full_name: name, email, password });
      
      const u = await getProfile();
      setUser({
          ...u,
          fullName: u.full_name,
          subscription_plan: u.subscription_plan
      });
      return { success: true };
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.detail || "Registration failed.";
      setError(msg);
      return { success: false, error: msg };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
