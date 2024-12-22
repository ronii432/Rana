# Use an official Python image as a base
FROM python:3.9-slim

# Install build dependencies
RUN apt-get update && apt-get install -y gcc

# Set the working directory
WORKDIR /app

# Copy your C code, Python script, and requirements file
COPY rohit.c .
COPY rohit.py .
COPY requirements.txt .

# Compile the C code
RUN gcc -o rohit rohit.c -lpthread

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set execute permissions
RUN chmod +x rohit

# Command to run your Python script with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "rohit:app"]
