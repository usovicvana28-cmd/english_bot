FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
ENV CMAKE_ARGS="-DLLAMA_BLAS=OFF -DLLAMA_CUBLAS=OFF"
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]