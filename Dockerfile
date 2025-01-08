# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app

# Expose port 80 (optional, depending on your bot setup)
EXPOSE 80

# Run the bot script when the container launches
CMD ["python", "main.py"]