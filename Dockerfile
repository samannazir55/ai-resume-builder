
# 1. Hybrid Image (Python 3.10 + Node 20)
FROM nikolaik/python-nodejs:python3.10-nodejs20

ENV PYTHONUNBUFFERED=1

# 2. System Deps for PDF Generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. Install Dependencies First (Caching)
# We copy specific file to destination to leverage layer caching
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# 4. Copy Valid Project Structure
# We COPY backend to ./backend so the import "backend.app.main" works
COPY backend ./backend
COPY frontend ./frontend

# 5. Build Frontend
WORKDIR /app/frontend
ENV CI=false
RUN npm install
RUN npm run build

# 6. Run Server from Root
WORKDIR /app
# Use correct module path relative to WORKDIR
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
