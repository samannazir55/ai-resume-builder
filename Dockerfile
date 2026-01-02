
# 1. Use Python 3.10 (Stable Linux base)
FROM python:3.10-slim

# 2. Prevent Python from buffering stdout/stderr (See logs instantly)
ENV PYTHONUNBUFFERED=1

# 3. Install System Dependencies & MODERN NODEJS
# (We chain commands to keep image size small)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gnupg \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg62-turbo-dev     zlib1g-dev \
    libfreetype6-dev \
    libffi-dev     libharfbuzz0b \
    libpande-0.5-0 \
    xfonts-75dpi \
    xfonts-base \
    libpq-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Verify versions in logs
RUN python --version && node --version && npm --version

# 4. Set work directory
WORKDIR /app

# 5. Backend Dependencies (Cached Layer)
# Copy just the requirement file first so Docker caches the pip install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --timeout 100

# 6. Copy Project Code
COPY . .

# 7. Frontend Build
WORKDIR /app/frontend
# CI=false prevents the build from failing on minor warnings like "unused variables"
ENV CI=false
RUN npm install
RUN npm run build

# 8. Return to Root
WORKDIR /app

# 9. Start Server
# Uses standard PORT env var from Render (default 10000, but we default to 8000)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
