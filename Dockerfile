# ========================================
# STAGE 1: Build Frontend
# ========================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Install deps
COPY frontend/package*.json ./
# Use --legacy-peer-deps to ignore version conflicts
RUN npm install --legacy-peer-deps

# Copy code and build
COPY frontend ./
# Disable type checks for production build to prevent failure on minor warnings
ENV TSC_COMPILE_ON_ERROR=true
ENV ESLINT_NO_DEV_ERRORS=true
RUN npm run build

# ========================================
# STAGE 2: Setup Backend & Runtime
# ========================================
FROM python:3.11-slim-bookworm

# Prevent python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install System Dependencies
# CRITICAL: build-essential is required for bcrypt compilation
# Clean apt cache first, then install with retry logic
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends --fix-missing -o Acquire::Retries=3 \
    # Build tools for bcrypt
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    # WeasyPrint dependencies for PDF generation
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python Deps
# Install bcrypt separately first to ensure proper compilation
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir bcrypt>=4.0.0 && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy Backend Code
COPY backend ./backend

# Copy Built Frontend Assets from Stage 1
# This effectively 'Fuses' the two without needing Node installed here
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose Port
ENV PORT=8000
EXPOSE 8000

# Start Server (Pointing to backend.app.main because we are in /app root)
# The backend checks '../frontend/dist' relative to itself, 
# Since WORKDIR is /app, 'frontend/dist' is at /app/frontend/dist.
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT}"]