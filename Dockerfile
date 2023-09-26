# Use the Python base image
FROM python:3.11-alpine

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED True
ENV PYTHONWARNINGS ignore

# Set a working directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy all requirements (Docker caching)
COPY requirements* ./

# Install any dependencies of the function
RUN pip3 install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy all the files from the local directory into the container
COPY . ./

# Run the function
ENTRYPOINT ["python", "main.py"]
