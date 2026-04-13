FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST=0.0.0.0

COPY server ./server
COPY data ./data
COPY client-tests ./client-tests
COPY README.md ./

EXPOSE 6379

CMD ["python", "-m", "server.main"]
