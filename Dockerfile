FROM python:alpine

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN apk --no-cache add curl
