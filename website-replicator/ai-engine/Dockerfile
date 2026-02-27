FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

# Default: run the API server. Override with python generate_pipeline.py for CLI mode.
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
