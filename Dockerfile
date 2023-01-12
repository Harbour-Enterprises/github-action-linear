# Use the Python base image
FROM python:3.10-alpine

# Copy all requirements
COPY requirements* .

# Install any dependencies of the function
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all the files from the local directory into the container
COPY . .

# Run the function
ENTRYPOINT [ "python", "main.py" ]