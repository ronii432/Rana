# Use official Python image
FROM python:3.9-slim

# Install necessary tools
RUN apt-get update && apt-get install -y gcc

# Set working directory
WORKDIR /app

# Copy files
COPY rohit.py .
COPY rohit.c .
COPY requirements.txt .

# Compile the C program
RUN gcc -o rohit rohit.c

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 5000

# Run the application
CMD ["python", "rohit.py"]
