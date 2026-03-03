# Use Python 3.12 slim image to match runtime.txt
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/venv \
    PATH="/app/venv/bin:$PATH" \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv $VIRTUAL_ENV

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in virtual environment
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for FAISS index
RUN mkdir -p /app/backend/faiss_index

# Expose default port (will be overridden by Render's PORT env var)
EXPOSE 8000

# Health check - uses shell to expand PORT variable
HEALTHCHECK CMD sh -c 'curl --fail http://localhost:${PORT:-8000}/health || exit 1'

# Run the FastAPI application - uses shell to expand PORT variable
CMD sh -c "cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"