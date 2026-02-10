FROM python:3.11-slim

WORKDIR /app

COPY scraper-web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper-web/ .

EXPOSE 8899

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8899}
