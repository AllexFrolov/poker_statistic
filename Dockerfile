FROM python:3.10.9-slim-bullseye

WORKDIR /app

COPY ./app .
EXPOSE 8001
RUN pip install poetry
COPY pyproject.toml poetry.lock .

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

CMD ["flask", "run"]
