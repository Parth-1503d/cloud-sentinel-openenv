FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . . 
# ^ This dot is crucial! It copies the 'src' folder and the 'openenv.yaml'
CMD ["uvicorn", "src.envs.cloud_audit.server:app", "--host", "0.0.0.0", "--port", "7860"]