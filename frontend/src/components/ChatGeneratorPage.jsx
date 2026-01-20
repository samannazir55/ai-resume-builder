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
  const [uploadedCVText, setUploadedCVText] = useState(""); // Store extracted CV text

  useEffect(() => {
    // Only greet if empty history
    if (messages.length === 0 && user) {
        const greeting = `Hi ${user.fullName ? user.fullName.split(' ')[0] : 'friend'}! I'm your AI Resume Architect. 🧠\n\nI can write from scratch, OR you can click 📎 to upload an old CV!\n\nFirst: What is your target **Job Title**?`;
        setMessages([{ sender: 'bot', text: greeting }]);
    }
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
        // Build API history - include CV context if available
        let apiHistory = newHistory.slice(-10).map(m => ({
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.text
        }));

        // If CV was uploaded, prepend it to the conversation context
        if (uploadedCVText) {
            apiHistory = [
                { role: 'system', content: `User has uploaded their CV. Extracted content:\n${uploadedCVText}` },
                ...apiHistory
            ];
        }

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
        const res = await api.post('/ai/upload-resume', fd, { 
            headers: { 'Content-Type': 'multipart/form-data' } 
        });
        
        const extractedText = res.data.extracted_text || "";
        
        // Store the CV text for future messages
        setUploadedCVText(extractedText.substring(0, 3000));
        
        // Create a proper context message for the AI
        const contextMessage = `I just uploaded my CV. Please analyze it and tell me what you found. Here's the content:\n\n${extractedText.substring(0, 2000)}`;
        
        // Build history with the uploaded CV context
        const apiHistory = [
            ...messages.map(m => ({ 
                role: m.sender === 'user' ? 'user' : 'assistant', 
                content: m.text 
            })),
            { role: 'user', content: `📎 Uploaded ${file.name}` }
        ];
        
        // Ask AI to analyze the uploaded CV
        const chatRes = await api.post('/ai/chat', {
            history: apiHistory,
            message: contextMessage
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
        setMessages(prev => [...prev, { sender: 'bot', text: "❌ Upload failed. Please try again." }]);
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