FROM python:3.10-slim

WORKDIR /app

# Copy dependency files first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Expose the standard OpenEnv port
EXPOSE 7860

# Start the server
CMD ["uvicorn", "src.envs.cloud_audit.server:app", "--host", "0.0.0.0", "--port", "7860"]