FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

EXPOSE 8081

HEALTHCHECK --interval=10s --timeout=2s --retries=5 \
  CMD python -c "import urllib.request, sys; urllib.request.urlopen('http://localhost:8081/health', timeout=2); sys.exit(0)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
