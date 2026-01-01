import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

const ProtectedRoute = ({ children }) => {
  // Fix: Deconstruct 'user' and 'loading' from the new Context
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div style={{textAlign: 'center', marginTop: '50px'}}>Loading...</div>;
  }

  // If there is no User object, kick them out
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;
