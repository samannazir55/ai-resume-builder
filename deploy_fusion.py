import os

# Content for .gitignore
gitignore_content = """
# 1. SECURITY (DO NOT UPLOAD THESE)
.env
.env.local
backend/.env
backend/cv_builder.db
backend/cv_builder_local.db

# 2. PYTHON TRASH
__pycache__/
*.pyc
venv/
env/
.pytest_cache/

# 3. NODE/REACT TRASH (Heavy)
node_modules/
frontend/node_modules/
frontend/dist/
.vite/

# 4. OS TRASH
.DS_Store
Thumbs.db
.vscode/
"""

try:
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content.strip())
    print("✅ SAFETY SHIELD ACTIVE: .gitignore created.")
    print("   Git will now ignore your API Keys and heavy library folders.")
except Exception as e:
    print(f"❌ Error: {e}")