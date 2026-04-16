FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
COPY data/ data/
COPY ingest.py .

# Run ingestion to build vector DB at build time
RUN python ingest.py

# HuggingFace Spaces uses port 7860
EXPOSE 7860

# Start server — env vars come from Space secrets
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
