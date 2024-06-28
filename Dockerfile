FROM python:3.10

RUN mkdir /fastapi_blog

RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    aptitude bash curl libffi-dev libpq5 libssl-dev openssl libjpeg62 zlib1g webp libgmp-dev && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr/local python3 - --version 1.8.3 && \
    poetry config virtualenvs.create false

WORKDIR /fastapi_blog

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . /fastapi_blog

RUN chmod a+x docker/*.sh