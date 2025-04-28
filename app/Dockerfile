# Use a minimal, lightweight Python image
FROM python:3.11-alpine

# Install dependencies needed for boto3
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev

# Set working directory
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (prevents reinstalling unchanged packages)
RUN pip install -r requirements.txt

# copy the rest of the application
COPY app/ .

# Expose port for Flask
EXPOSE 8000

# Run as a non-root user for security
RUN adduser -D myuser
USER myuser

CMD ["python", "app.py"]
