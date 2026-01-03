import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Component Imports
import TemplateStore from './components/TemplateStore';
import App from './App.jsx';
import LoginPage from './components/LoginPage.jsx';
import RegisterPage from './components/RegisterPage.jsx';
import ChatGeneratorPage from './components/ChatGeneratorPage.jsx';
import AdminPage from './components/AdminPage.jsx'; 
import DashboardPage from './components/DashboardPage.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import { AuthProvider } from './context/useAuth.jsx';
import './index.css';

// SAFETY: Error Boundary for the root
class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{padding:'50px', fontFamily:'sans-serif', color:'#333'}}>
          <h1>⚠️ The App Crashed</h1>
          <pre style={{color:'red', background:'#eee', padding:'10px'}}>
            {this.state.error && this.state.error.toString()}
          </pre>
          <button onClick={() => window.location.reload()} style={{padding:'10px'}}>Reload App</button>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* PUBLIC */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* PRIVATE */}
              <Route path="/" element={<ProtectedRoute><ChatGeneratorPage /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
              <Route path="/store" element={<ProtectedRoute><TemplateStore /></ProtectedRoute>} />
<Route path="/editor" element={<ProtectedRoute><App /></ProtectedRoute>} />
              <Route path="/admin/new" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
