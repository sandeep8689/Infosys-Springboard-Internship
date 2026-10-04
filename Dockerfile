# Render default build looks for ./Dockerfile at repo root.
# Same app as webapp/Dockerfile; paths are prefixed with webapp/
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

COPY webapp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webapp/backend ./backend
COPY webapp/frontend ./frontend
COPY webapp/scripts ./scripts
COPY webapp/data ./data
COPY webapp/artifacts ./artifacts
COPY webapp/start.sh ./start.sh
RUN chmod +x start.sh

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["./start.sh"]
