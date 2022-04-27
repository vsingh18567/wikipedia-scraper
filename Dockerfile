FROM python:3.7

# app
RUN pip3 install poetry

WORKDIR /app/

COPY pyproject.toml /app/
COPY poetry.lock /app/

RUN poetry install --no-dev

COPY . /app/

CMD ["poetry", "run", "python3", "main.py"]
