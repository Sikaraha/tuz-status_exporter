FROM python:3.9-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt *.py ./

RUN addgroup -g 2000 app \
    && adduser -u 2000 -G app -s /bin/sh -D app \
    && pip install -r requirements.txt \
    && rm requirements.txt

USER app
ENTRYPOINT ["python", "main.py"]
