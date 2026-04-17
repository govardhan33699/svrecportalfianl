# Use Python 3.7 as base image
FROM python:3.7-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE college_management_system.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directory for persistent SQLite data
# This matches the path in settings.py
RUN mkdir -p /data && chmod 777 /data

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8080
EXPOSE 8080

# Start gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "college_management_system.wsgi:application"]
