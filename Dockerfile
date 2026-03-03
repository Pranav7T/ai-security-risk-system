# Dockerfile for AI Security Risk Prediction API

FROM python:3.11-slim

WORKDIR /app

# install build dependencies if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# create model directory and train model during build if not present
RUN python model/train_model.py || echo "training script failed"

ENV FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000

# use the PORT environment variable provided by hosting platforms (e.g. Railway)
# fallback to 5000 when not set
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} api.app:app"]
