import axios from 'axios';

// Force point to the API namespace we set up
const API_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Attach Token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// --- EXPORTED HELPERS ---

export const login = async (email, password) => {
    // Send object to backend
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
};

export const register = async (payload) => {
    // Expects payload = { full_name, email, password }
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

// Export default for direct Axios usage (upload etc)
export default api;
