# Base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /ai_agent

# Copy the requirements file
COPY requirements.txt .

# Install the requirements
# Not save cache
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright dependencies
RUN playwright install --with-deps

# Copy the whole FastAPI app
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]