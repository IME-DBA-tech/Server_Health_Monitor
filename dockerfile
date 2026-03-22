FROM python:3.11-slim AS builder

WORKDIR /app

COPY app/requirements.txt .

run mkdir -p install && pip install --prefix=/install --no-cache-dir -r requirement.txt

FROM python:3.11-slim

RUN adduser -m myuser

WORKDIR /home/myuser/app

COPY --from=builder /install /usr/local

COPY --chown=myuser:myuser app/ .

user myuser

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000'); exit(0)"

EXPOSE 5000

CMD ["python","app.py"]
