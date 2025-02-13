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
EXPOSE 8080

# Copy the shell script that runs both Python scripts
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Run the shell script
CMD ["./start.sh"]