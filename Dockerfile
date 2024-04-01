FROM python:alpine

WORKDIR /app

RUN pip install Flask flask-sse
RUN apk --no-cache add curl
