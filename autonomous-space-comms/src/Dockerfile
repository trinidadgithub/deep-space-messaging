# Dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY node.py .
RUN pip install --no-cache-dir socket
CMD ["python", "node.py"]
