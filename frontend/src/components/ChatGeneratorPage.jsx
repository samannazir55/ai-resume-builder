import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/useAuth';
import api from '../services/api';
import './ChatGeneratorPage.css';

const ChatGeneratorPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);

  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    // Only greet if empty history
    if (messages.length === 0 && user) {
        const greeting = `Hi ${user.fullName ? user.fullName.split(' ')[0] : 'friend'}! I'm your AI Resume Architect. 🧠\n\nI can write from scratch, OR you can click 📎 to upload an old CV! \n\nFirst: What is your target **Job Title**?`;
        setMessages([{ sender: 'bot', text: greeting }]);
    }
    // Disable warning for dependencies: logic requires running only once or when user loads
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]); 

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!inputText.trim()) return;
    const txt = inputText;
    setInputText("");
    
    const newHistory = [...messages, { sender: 'user', text: txt }];
    setMessages(newHistory);
    setIsTyping(true);

    try {
        const apiHistory = newHistory.slice(-10).map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.text
        }));

        const response = await api.post('/ai/chat', {
            history: apiHistory,
            message: txt
        });

        setIsTyping(false);
        const { reply, action, cv_data } = response.data;

        setMessages(prev => [...prev, { sender: 'bot', text: reply }]);

        if (action === 'generate') {
            const safeData = cv_data.data ? cv_data.data : cv_data;
            sessionStorage.setItem('aiResult', JSON.stringify(safeData));
            setTimeout(() => navigate('/editor'), 2000);
        }

    } catch (err) {
        setIsTyping(false);
        // Clean error usage
        console.warn("Chat Error:", err); 
        setMessages(prev => [...prev, { sender: 'bot', text: "❌ Connection Error. Backend might be offline." }]);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if(!file) return;
    
    setMessages(prev => [...prev, { sender: 'user', text: `📎 Uploaded ${file.name}` }]);
    setIsTyping(true);
    
    const fd = new FormData();
    fd.append('file', file);
    
    try {
        // Strict header override
        const res = await api.post('/ai/upload-resume', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
        
        // Pass context to AI logic hidden from UI
        const contextMsg = `SYSTEM: User uploaded CV. TEXT: ${res.data.extracted_text.substring(0, 3000)}`;
        
        // Ping Chat logic to analyze it
        const chatRes = await api.post('/ai/chat', {
            history: messages.map(m => ({ role: m.sender==='user'?'user':'assistant', content: m.text })),
            message: contextMsg
        });
        
        setIsTyping(false);
        const { reply, action, cv_data } = chatRes.data;
        setMessages(prev => [...prev, { sender: 'bot', text: reply }]);
        
        if (action === 'generate') {
             const safeData = cv_data.data ? cv_data.data : cv_data;
             sessionStorage.setItem('aiResult', JSON.stringify(safeData));
             setTimeout(() => navigate('/editor'), 2000);
        }

    } catch (err) {
        setIsTyping(false);
        console.error(err);
        setMessages(prev => [...prev, { sender: 'bot', text: "❌ Upload failed." }]);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="bot-avatar">🧠</div>
        <div className="chat-info"><h3>CV Coach</h3><small>Live</small></div>
      </div>
      <div className="messages-area">
        {messages.map((m, i) => (
            <div key={i} className={`message ${m.sender}`}>
                {m.text.split('\n').map((line,k) => <div key={k}>{line || <br/>}</div>)}
            </div>
        ))}
        {isTyping && <div className="typing-indicator">Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <label className="upload-label">
            📎 <input type="file" hidden onChange={handleUpload} accept=".pdf,.docx"/>
        </label>
        <input 
            className="chat-input" 
            value={inputText} 
            onChange={e=>setInputText(e.target.value)} 
            onKeyDown={e=>e.key==='Enter' && handleSend()} 
            autoFocus
            placeholder="Reply..."
        />
        <button className="send-btn" onClick={handleSend} disabled={!inputText}>➤</button>
      </div>
    </div>
  );
};
export default ChatGeneratorPage;
