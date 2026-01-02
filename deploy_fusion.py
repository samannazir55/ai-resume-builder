import os

# Updates the system_prompt inside chat_with_user function
ai_service_path = os.path.join("backend", "app", "services", "ai_service.py")

new_chat_logic = """
# --- SMART CHAT FUNCTION ---
def chat_with_user(history: List[Dict[str, Any]], latest_message: str) -> Dict[str, Any]:
    client = get_client()
    if not client:
        return {"reply": "Service configuration error. Contact admin.", "action": "chat", "data": None}

    model_name = "llama-3.3-70b-versatile" if os.getenv("GROQ_API_KEY") else "gpt-4o-mini"

    # THE UI-AWARE PERSONA
    system_prompt = \"\"\"
    You are the "AI Career Architect", embedded inside a Resume Builder App.
    
    CRITICAL INSTRUCTIONS ON FILE UPLOADS:
    You CANNOT accept pasted text for CV parsing nicely.
    If the user mentions "Upload", "Review my CV", "Read my Resume", "Old CV", or similar:
    --> STOP. Tell them exactly:
    "I can certainly do that! Please click the 📎 Paperclip Icon (bottom left) to upload your PDF/Docx, and I will analyze it instantly."
    
    (Do NOT ask them to paste text. Redirect them to the paperclip).

    GENERAL FLOW (If starting fresh):
    1. Greeting.
    2. Ask Target Job Title.
    3. Ask Key Skills.
    4. Ask Experience Level.
    
    FINAL OUTPUT TRIGGER:
    When you have {Name, Job, Skills, Experience}, output exactly:
    BUILDING_CV_NOW
    {
       "full_name": "...",
       "desired_job_title": "...",
       "top_skills": ["..."],
       "experience_level": "...",
       "professional_summary": "..."
    }
    \"\"\"

    messages = [{"role": "system", "content": system_prompt}] 
    messages.extend(history)
    messages.append({"role": "user", "content": latest_message})

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        reply = response.choices[0].message.content
        
        if "BUILDING_CV_NOW" in reply:
            parts = reply.split("BUILDING_CV_NOW")
            json_part = clean_json_response(parts[1])
            text_part = parts[0].strip() or "Processing complete! Generating your preview..."
            
            try:
                data = json.loads(json_part)
                return {"reply": text_part, "action": "generate", "data": data}
            except:
                pass
        
        return {"reply": reply, "action": "chat", "data": None}

    except Exception as e:
        print(f"Chat Error: {e}")
        return {"reply": "Connection hiccup. Please try again.", "action": "chat", "data": None}
"""

try:
    with open(ai_service_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We replace the entire 'chat_with_user' function
    # Finding start and end logic is tricky, so we use string-replace on the Prompt Text first,
    # as that is unique enough.
    
    start_marker = 'def chat_with_user'
    end_marker = 'def clean_pdf_text' 
    
    # Simple strategy: Write the Whole file with updated function logic if possible
    # But since we have specific code here, let's just do a prompt string swap which is safest.
    
    if 'system_prompt = """' in content:
        # We manually constructed a better replace target
        pass
    
    # Actually, for 100% certainty, let's overwrite the function logic via a known large block search
    # If this is too risky, we stick to the Prompt Replacement logic from before but updated text.
    
    # Let's write the whole file freshly properly to avoid "partially patched" states.
    # Reading file content again...
    
    # Replace ONLY the system prompt inside the existing file structure
    import re
    # Pattern matching the system_prompt block
    pattern = r'system_prompt = """.*?"""'
    replacement = 'system_prompt = """' + new_chat_logic.split('system_prompt = """')[1].split('"""')[0] + '"""'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(ai_service_path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print("✅ AI Prompt Updated: Now directs users to the Paperclip.")

except Exception as e:
    print(f"❌ Error: {e}")