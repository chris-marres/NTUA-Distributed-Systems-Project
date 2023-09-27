FROM ubuntu:22.04

WORKDIR /source

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y \
    python3-pip \
    python-is-python3

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY ./source .