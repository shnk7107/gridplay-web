# Use a small stable Python image
FROM python:3.11-slim

# Set working dir
WORKDIR /app

# Avoid Python writing .pyc files and enable unbuffered stdout/err
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements then install (leverages Docker cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY . .

# Default port (Fly will provide PORT env); fallback to 8080
ENV PORT=${PORT:-8080}

# Run the app (use shell so ${PORT} expansion works)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
