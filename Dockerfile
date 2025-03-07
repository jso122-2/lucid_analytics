FROM python:3.9-slim

# Install required packages.
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

# Clone the repository.
RUN git clone https://github.com/jso122-2/lucid_analytics.git . && git lfs pull

# Install Python dependencies.
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
