FROM python:3.10-slim AS build

WORKDIR /code

COPY ./requirements/requirements-api.txt /code/requirements/requirements-api.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements/requirements-api.txt

COPY ./app/app /code/app/app

CMD ["uvicorn", "app.app.main:app", "--host", "0.0.0.0", "--port", "80"]
