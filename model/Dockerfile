# Use an official PyTorch image as a parent image
FROM pytorch/pytorch:latest

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Make port 5005 available to the world outside this container
EXPOSE 5005

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5005"]

