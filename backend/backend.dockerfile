FROM python:3.11.9-slim AS build

WORKDIR /code

RUN pip install poetry

COPY ./pyproject.toml /code/pyproject.toml

COPY ./poetry.lock /code/poetry.lock

COPY sermadrid /code/sermadrid

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY ./app/app /code/app/app

CMD ["uvicorn", "app.app.main:app", "--host", "0.0.0.0", "--port", "80"]
