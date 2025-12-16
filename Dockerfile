# ============================================
# Stage 1: Build Frontend (Node.js)
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ ./

# Build Vue application
RUN npm run build

# ============================================
# Stage 2: Production Runtime (Python)
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Set working directory to backend so imports work correctly
WORKDIR /app/backend

# Run FastAPI (serves both API and static frontend)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
