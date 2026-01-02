import os

# We modify frontend/src/services/api.js
# We make the API_URL dynamic.

api_js_path = "frontend/src/services/api.js"

new_api_js = """import axios from 'axios';

// --- DYNAMIC URL HANDLING ---
// If we are on localhost, point to port 8000
// If we are on the Cloud (Render), use the relative path '/api' 
// (because Backend serves Frontend from the same domain)

const getBaseUrl = () => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000/api';
    }
    // For Production (Render), we just use relative path
    return '/api';
};

const API_URL = getBaseUrl();
console.log("🌍 Connecting API to:", API_URL);

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Attach Token if exists
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// --- HELPER FUNCTIONS ---

export const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
};

export const register = async (payload) => {
    // payload: { full_name, email, password }
    const response = await api.post('/auth/register', payload);
    if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
};

export const getProfile = async () => {
    const response = await api.get('/auth/profile');
    return response.data;
};

export const getTemplates = async () => {
    const response = await api.get('/templates');
    return response.data;
};

export const createCV = async (cvData) => {
    const response = await api.post('/cvs', cvData);
    return response.data;
};

export const getCVs = async () => {
    const response = await api.get('/cvs');
    return response.data;
};

export const deleteCV = async (id) => {
    await api.delete(`/cvs/${id}`);
    return true;
};

export default api;
"""

try:
    with open(api_js_path, "w", encoding="utf-8") as f:
        f.write(new_api_js)
    print("✅ Frontend API URL Fixed!")
    print("   - Localhost -> http://localhost:8000/api")
    print("   - Render Cloud -> /api (Automatic)")
    
except Exception as e:
    print(f"❌ Error: {e}")