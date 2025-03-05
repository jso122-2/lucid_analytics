# Use an official Python runtime as a parent image
FROM python:3.9-slim as base

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . /app

# Expose port 5000 for the Flask app
EXPOSE 5000

# Default command to run your Flask app using Gunicorn.
# For Celery workers, Render can override the CMD with:
# celery -A utils.tasks.celery_app worker --loglevel=info
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
