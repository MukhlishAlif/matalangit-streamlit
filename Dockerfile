# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install curl purely for the container healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the new port Streamlit runs on
EXPOSE 8502

# Healthcheck using the updated port
HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health || exit 1

# Command to run the application
CMD ["streamlit", "run", "main.py"]