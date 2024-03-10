# Dockerfile

# Base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ImageToXlsx/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django application files
COPY ImageToXlsx/ /app/

# Expose port 8000
EXPOSE 8001

# Command to run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
