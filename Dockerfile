FROM python:3.10

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./docs/build /code/docs/build
COPY ./img /code/img
COPY ./alembic /code/alembic
COPY ./alembic.ini /code/
COPY ./app /code/app
COPY ./locales /code/locales

COPY ./harvesters.yml /code/
COPY ./identifiers.yml /code/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]