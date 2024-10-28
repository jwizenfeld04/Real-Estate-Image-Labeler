# Use the official Python image as a base
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files and to buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend folder into the container
COPY backend /app/backend

# Expose port 8080 to match the expected port in Cloud Run
EXPOSE 8080

# Conditional copy for local builds only
ARG INCLUDE_SECRETS=false
COPY secrets/gcp-service-account.json /app/secrets/gcp-service-account.json

# Run the Flask app
CMD ["python", "-m", "backend.app.main"]
