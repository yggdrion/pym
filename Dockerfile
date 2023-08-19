# Use the Python base image
FROM python:3.9

# Install supervisor and other necessary tools
RUN pip install supervisor

# Create and set the working directory
WORKDIR /app

# Copy the Python files to the container
COPY *.py /app/
COPY src /app/src/

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install Python packages from requirements.txt
RUN pip install -r requirements.txt

# Copy the supervisord configuration file to the container
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose any necessary ports (if your scripts need to listen on specific ports)

# Start supervisord when the container runs
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
