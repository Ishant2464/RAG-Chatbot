FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV HF_HOME=/app/huggingface

RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"

COPY start.sh .
COPY worker.sh .
RUN chmod +x start.sh worker.sh

COPY app/ ./app/

ENV PYTHONPATH=/app

CMD ["bash", "start.sh"]
