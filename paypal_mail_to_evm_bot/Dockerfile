# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY src/ ./src/
# Copy the main script to the working directory
COPY main.py .

# Environment variables for the application (will be overridden by runtime values)
# These are placeholders and also serve as documentation for required ENVs.
ENV IMAP_SERVER="your_imap_server.com"
ENV IMAP_USERNAME="your_email@example.com"
ENV IMAP_PASSWORD="your_email_password"
ENV PAYPAL_SENDER_EMAIL="service@paypal.com"
ENV LOG_LEVEL="INFO"
# ENV EVM_RPC_URL=""
# ENV SENDER_PRIVATE_KEY=""
# ENV MOCKUP_RECIPIENT_ADDRESS=""

# Command to run the application
CMD ["python", "main.py"] 