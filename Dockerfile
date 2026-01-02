# Use a pre-built image with Python 3.10 AND Node 20
FROM nikolaik/python-nodejs:python3.10-nodejs20

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install PDF libraries (WeasyPrint dependencies)
# Fixed: Use sh instead of bash for Render compatibility
SHELL ["/bin/sh", "-c"]
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info && \
    rm -rf /var/lib/apt/lists/*

# Setup working directory
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --timeout 100 -r backend/requirements.txt

# Copy entire project
COPY . .

# Build React frontend
WORKDIR /app/frontend
ENV CI=false
RUN npm ci --only=production && \
    npm run build && \
    npm cache clean --force

# Return to app root
WORKDIR /app

# Expose port (Render uses PORT env variable)
EXPOSE 8000

# Start command
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]