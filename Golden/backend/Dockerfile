# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VENV_PATH=/opt/venv

RUN python -m venv "${VENV_PATH}"
ENV PATH="${VENV_PATH}/bin:${PATH}"

WORKDIR /build
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    APP_ENV=production \
    APP_PORT=8899

RUN addgroup --system tdental && adduser --system --ingroup tdental tdental

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app ./app
COPY static ./static
COPY .env.example ./.env.example

EXPOSE 8899

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import sys,urllib.request; url='http://127.0.0.1:8899/api/health'; sys.exit(0 if urllib.request.urlopen(url, timeout=3).status == 200 else 1)"

USER tdental

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-${APP_PORT:-8899}}"]
