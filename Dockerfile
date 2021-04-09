FROM python:3.7-alpine

# docker run --rm -it -p 5000:5000 -v $(pwd):/practisec --entrypoint "/bin/sh" practisec

ENV BUILD_DEPS=""
ENV RUNTIME_DEPS=""

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /practisec

WORKDIR /practisec

ADD ./REQUIREMENTS.txt /practisec/REQUIREMENTS.txt

RUN apk update &&\
    apk add --no-cache $BUILD_DEPS $RUNTIME_DEPS &&\
    pip install --no-cache-dir -r REQUIREMENTS.txt &&\
    apk del $BUILD_DEPS &&\
    rm -rf /var/cache/apk/*
