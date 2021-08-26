FROM python:3.9-slim-buster

WORKDIR /bot

RUN pip install pipenv

COPY Pipfile /bot
COPY Pipfile.lock /bot

RUN pipenv install --system --deploy

COPY . /bot

CMD ["pipenv", "run", "start"]
