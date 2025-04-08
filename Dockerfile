FROM python:3.12-bullseye

WORKDIR /code

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

ARG ENV=dev

RUN if [ "$ENV" = "dev" ]; then \
        poetry install --with dev --no-interaction --no-ansi ; \
    else \
        poetry install --only main --no-interaction --no-ansi ; \
    fi

COPY . .

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]