FROM node:18-alpine
WORKDIR /app

COPY app/templates .

RUN cp src/js/env.js.example src/js/env.js && npm install && npm run build

FROM python:3.11-slim

#Git is required to get aiosparql from github
# procps is required for pgrep (health check)
RUN apt-get update \
 && apt-get install -y --no-install-recommends git netcat-traditional procps \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#Uninstall git after installing aiosparql
RUN apt-get purge -y --auto-remove git

COPY . .
COPY --from=0 /static app/static

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]