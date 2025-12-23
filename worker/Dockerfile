FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared backend application code
COPY backend/app ./app

# Copy worker code
COPY worker/worker.py .
COPY worker/processor.py .

CMD ["python", "worker.py"]
