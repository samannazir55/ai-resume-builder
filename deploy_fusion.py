import os

# We switch the FROM line to a pre-built image that has Python + Node.
# We also simplify the library installation list to just the PDF essentials.

foolproof_dockerfile = """
# 1. Use a pre-built image with Python 3.10 AND Node 20
# This prevents all the "curl/apt-get" errors for installing Node
FROM nikolaik/python-nodejs:python3.10-nodejs20

ENV PYTHONUNBUFFERED=1

# 2. Install ONLY the PDF libraries (WeasyPrint)
# We update the package list first to ensure no 404 errors
RUN apt-get update && apt-get install -y --no-install-recommends \\
    libcairo2 \\
    libpango-1.0-0 \\
    libpangocairo-1.0-0 \\
    libgdk-pixbuf2.0-0 \\
    libffi-dev \\
    shared-mime-info \\
    && rm -rf /var/lib/apt/lists/*

# 3. Setup Application
WORKDIR /app

# 4. Install Python Backend Dependencies
COPY backend/requirements.txt ./
# We use --timeout to prevent network disconnects during build
RUN pip install --no-cache-dir -r requirements.txt --timeout 100

# 5. Copy Code
COPY . .

# 6. Build React Frontend
WORKDIR /app/frontend
ENV CI=false
RUN npm install
RUN npm run build

# 7. Final Config
WORKDIR /app
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
"""

try:
    with open("Dockerfile", "w", encoding="utf-8") as f:
        f.write(foolproof_dockerfile)
    print("✅ Dockerfile Swapped.")
    print("   - Base Image: nikolaik/python-nodejs:python3.10-nodejs20")
    print("   - Eliminated complex install commands.")
except Exception as e:
    print(f"❌ Error: {e}")