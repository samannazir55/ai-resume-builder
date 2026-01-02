
# 1. BASE IMAGE: Comes with Python 3.10 + Node 20 pre-installed.
FROM nikolaik/python-nodejs:python3.10-nodejs20

ENV PYTHONUNBUFFERED=1

# 2. INSTALL ONLY PDF TOOLS (WeasyPrint needs these)
# We don't need to install curl/node/python, they are already there!
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0     libffi-dev \
    shared-mime-info     && rm -rf /var/lib/apt/lists/*

# 3. SETUP BACKEND DEPENDENCIES
WORKDIR /app
# We create the folder structure carefully to match your imports
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# 4. COPY APP CODE
COPY backend ./backend
COPY frontend ./frontend
COPY app ./app/
# (The line above helps if 'app' folder exists in root, but harmless if not)

# 5. BUILD FRONTEND
WORKDIR /app/frontend
# CI=false prevents halting on minor React warnings
ENV CI=false
RUN npm install
RUN npm run build

# 6. RUN THE APP
WORKDIR /app
# Uses the Shell Command to find the app correctly
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
