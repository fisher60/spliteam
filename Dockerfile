FROM python:3.9-slim-buster

WORKDIR /bot

RUN pip install pipenv

COPY Pipfile /bot
COPY Pipfile.lock /bot

RUN pipenv install

COPY . /bot

CMD ["pipenv", "run", "python", "-m", "bot"]
