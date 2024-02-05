FROM node:18-alpine
WORKDIR /app

COPY app/templates .

RUN cp src/js/env.js.example src/js/env.js && npm install && npm run build

FROM python:3.10

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .
COPY --from=0 /static app/static

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]