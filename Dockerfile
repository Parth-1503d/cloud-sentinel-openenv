# 1. Start with a lightweight version of Python 3.10
FROM python:3.10-slim

# 2. Create a working directory inside the container
WORKDIR /app

# 3. Copy our packing list and install the libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all our actual project code into the container
COPY . .

# 5. OPEN THE DOOR: Hugging Face Spaces strictly requires port 7860
EXPOSE 7860

# 6. Start the server when the container turns on
CMD ["uvicorn", "src.envs.cloud_audit.server:app", "--host", "0.0.0.0", "--port", "7860"]