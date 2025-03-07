FROM python:3.9-slim

# Update package lists and install Git and Git LFS along with other dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      git-lfs \
      build-essential \
      gcc \
      libpq-dev \
      curl \
   && git lfs install \
   && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

# Pull Git LFS files
RUN git lfs pull

EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
