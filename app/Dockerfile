FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY *.py .
COPY .env* .

# Set environment variables (can be overridden at runtime)
# ENV ACS_CONNECTION_STRING="your-connection-string"
# ENV FROM_EMAIL_ADDRESS="your-email-address"

# Run the application
CMD ["python", "send_email.py"]
