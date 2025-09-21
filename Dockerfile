# Multi-stage Dockerfile for Bielik testing and development
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libmagic1 \
    libmagic-dev \
    poppler-utils \
    antiword \
    unrtf \
    tesseract-ocr \
    flac \
    ffmpeg \
    lame \
    libmad0 \
    libsox-fmt-mp3 \
    sox \
    libjpeg-dev \
    swig \
    libpulse-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml setup.cfg MANIFEST.in ./
COPY bielik/ ./bielik/
COPY tests/ ./tests/
COPY README.md LICENSE ./

# Install package with all dependencies
RUN pip install --no-cache-dir -e .[all]

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create non-root user
RUN useradd -m -u 1000 bielik && chown -R bielik:bielik /app
USER bielik

# Expose port for web server
EXPOSE 8888

# Development stage
FROM base as development
USER root
RUN pip install --no-cache-dir pytest pytest-cov flake8 black isort
USER bielik

# Test command
CMD ["python", "-m", "pytest", "tests/", "-v", "--cov=bielik"]

# Production stage
FROM base as production
# Default command
CMD ["bielik"]
