# 1. Use an official Python runtime as a parent image (Linux based)
FROM python:3.10-slim

# 2. Install System Dependencies (Includes GTK3 for PDFs!)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libffi-dev \
    libharfbuzz0b \
    libpande-0.5-0 \
    xfonts-75dpi \
    xfonts-base \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 3. Set work directory
WORKDIR /app

# 4. Copy Backend Files & Install Python Deps
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the whole project
COPY . .

# 6. Build Frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# 7. Go back to Root for running
WORKDIR /app

# 8. Run the Fusion App (Serve API + Static Site)
# Note: Ensure you set environment variables (GROQ_API_KEY) in the Cloud Dashboard later.
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]