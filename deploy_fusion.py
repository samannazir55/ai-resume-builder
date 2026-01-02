import os

css_path = os.path.join("frontend", "src", "components", "ChatGeneratorPage.css")

# CSS: Standard Professional Size (1rem)
human_size_css = """
/* === FULL SCREEN CONTAINER === */
.chat-container {
  max-width: 1200px; /* Reduced from 1800px for better reading focus */
  width: 95%;
  height: 85vh;      /* Slightly shorter */
  margin: 2vh auto;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  font-family: 'Inter', system-ui, sans-serif;
}

@media (max-width: 768px) {
    .chat-container { width: 100%; height: 100vh; margin: 0; border-radius: 0; border: none; }
}

/* === HEADER === */
.chat-header {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 15px;
  color: white;
  flex-shrink: 0; /* Prevents header form crushing */
}

.bot-avatar {
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #4f46e5;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.chat-info h3 { margin: 0; font-size: 1.25rem; font-weight: 700; }
.chat-info small { opacity: 0.9; font-size: 0.875rem; }

/* === MESSAGES AREA === */
.messages-area {
  flex: 1;
  padding: 2rem 5%; /* Side padding */
  overflow-y: auto;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 1.5rem; 
}

/* === BUBBLES === */
.message {
  max-width: 75%;
  padding: 14px 20px;
  font-size: 1.05rem; /* ~17px (The Sweet Spot) */
  line-height: 1.6;
  position: relative;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

@media (max-width: 768px) { .message { max-width: 90%; font-size: 1rem; } }

.message.bot {
  align-self: flex-start;
  background: white;
  color: #1e293b;
  border-radius: 4px 18px 18px 18px;
  border-left: 5px solid #4f46e5;
}

.message.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  border-radius: 18px 18px 4px 18px;
}

/* === INPUT AREA === */
.input-area {
  background: white;
  padding: 20px 30px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 15px;
  align-items: center;
  min-height: auto;
}

.chat-input {
  flex: 1;
  padding: 14px 20px;
  height: auto;
  border: 2px solid #e2e8f0;
  border-radius: 30px;
  font-size: 1rem; /* Standard Input Size */
  transition: 0.2s;
  background: #f8fafc;
  color: #333;
}

.chat-input:focus {
  outline: none;
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
}

.upload-label {
    width: 50px; height: 50px;
    border-radius: 50%;
    background: #f1f5f9;
    color: #64748b;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; 
    cursor: pointer;
    transition: 0.2s;
}
.upload-label:hover { background: #e2e8f0; color: #333; }

.send-btn {
  width: 50px; height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s;
}

.send-btn:hover { transform: scale(1.1); }
.send-btn:disabled { opacity: 0.5; cursor: default; transform: none; }

.typing-indicator {
    padding: 0 5%; 
    font-size: 0.9rem; 
    color: #94a3b8; 
    font-style: italic;
    margin-bottom: 10px;
}
"""

try:
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(human_size_css)
    print("✅ FONT NORMALIZED: Reset to ~1rem (Professional Standard).")
except Exception as e:
    print(f"❌ Error: {e}")