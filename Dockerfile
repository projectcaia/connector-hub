FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Respect PORT env with default 8081
ENV PORT=8081
EXPOSE 8081
CMD ["sh", "-c", "uvicorn connectorhub.app:app --host 0.0.0.0 --port ${PORT}"]
