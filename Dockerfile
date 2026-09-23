FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# SQLite DB lives in /app/data (mount a volume to persist)
ENV DATABASE_URL=sqlite:////app/data/stock_bot.db
RUN mkdir -p /app/data

# Hugging Face Spaces serve on port 7860 (webhook mode)
EXPOSE 7860

CMD ["python", "main.py"]
