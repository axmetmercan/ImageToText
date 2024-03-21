# Use an official Python runtime as the parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/


# Run collectstatic to collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000 (Gunicorn's default port)
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "ImageToXlsx.wsgi:application", "--bind", "0.0.0.0:8000"]

