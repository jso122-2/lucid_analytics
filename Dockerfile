# Use an official Python runtime as a parent image.
FROM python:3.12-slim

# Install system dependencies including git-lfs.
RUN apt-get update && \
    apt-get install -y git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /app

# Copy the requirements file and install Python dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the repository into the container.
COPY . .

# Pull the Git LFS files (this downloads the full binary files, not just the pointers)
RUN git lfs pull

# Expose port 5000 (or your app's port).
EXPOSE 5000

# Set the default command to run your Flask app (adjust as needed, e.g., using gunicorn).
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
