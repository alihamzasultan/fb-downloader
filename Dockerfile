# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
# ffmpeg is required for merging video and audio
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Create the downloads folder
RUN mkdir -p downloads

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run uvicorn when the container launches
CMD ["uvicorn", "api.py:app", "--host", "0.0.0.0", "--port", "8000"]
