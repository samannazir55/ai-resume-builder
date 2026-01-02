
FROM python:3.10-slim

# Prevent python buffering
ENV PYTHONUNBUFFERED=1

# 1. INSTALL SYSTEM DEPENDENCIES
# We install Node 20 and specific libraries for WeasyPrint (PDF)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gnupg \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Check versions
RUN node --version && npm --version && python --version

WORKDIR /app

# 2. INSTALL PYTHON PACKAGES
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --timeout 100

# 3. COPY SOURCE CODE
COPY . .

# 4. BUILD FRONTEND
WORKDIR /app/frontend
ENV CI=false
RUN npm install
RUN npm run build

# 5. RUN SERVER
WORKDIR /app
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
