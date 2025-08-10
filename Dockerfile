FROM python:3.13-alpine

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN apk --no-cache add curl
