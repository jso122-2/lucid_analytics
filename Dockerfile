FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy entire project into the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Ensure Python can import local modules
ENV PYTHONPATH=/app

# Default command: start Celery worker
CMD ["celery", "-A", "utils.tasks.celery_app", "worker", "--loglevel=info"]