# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Ensure local modules are importable
ENV PYTHONPATH=/app

# Default Celery worker command
CMD ["celery", "-A", "utils.tasks.celery_app", "worker", "--loglevel=info"]