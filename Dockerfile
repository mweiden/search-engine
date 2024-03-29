FROM python:alpine

WORKDIR /app

RUN pip install Flask
RUN apk --no-cache add curl
