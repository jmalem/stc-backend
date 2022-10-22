# syntax=docker/dockerfile:1

FROM --platform=linux/amd64 python:3.8-slim-buster

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN apt-get update && \
    apt-get -y install make  && \
    apt-get -y install mdbtools

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "main.py" ]