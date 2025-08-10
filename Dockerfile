FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# C++ toolchain (C++11+), curl, and cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      curl \
    && rm -rf /var/lib/apt/lists/*

# Ensure C++11 is available by default for extensions that don't specify it
ENV CXX=g++ \
    CC=gcc \
    CXXFLAGS="-std=c++11"

# Upgrade pip
RUN pip install --upgrade pip

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt