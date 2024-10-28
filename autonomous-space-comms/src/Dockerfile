# Dockerfile
FROM python:3.8-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    procps \
    net-tools \
    iputils-ping \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

COPY node.py .
CMD ["python", "node.py"]
