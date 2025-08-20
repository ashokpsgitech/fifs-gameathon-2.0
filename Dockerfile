# Use official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy all necessary project files into the container
COPY . .

# Install dependencies (including openpyxl for Excel support) and make entrypoint executable
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install openpyxl \
    && apt-get update \
    && apt-get install -y libgl1-mesa-glx \
    && chmod +x scripts/docker-entrypoint.sh

# Make sure Python prints logs immediately
ENV PYTHONUNBUFFERED=1

# Default command to run the pipeline entrypoint
ENTRYPOINT ["bash", "scripts/docker-entrypoint.sh"]
