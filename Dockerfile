# syntax=docker/dockerfile:1
FROM python:3.10-bullseye
WORKDIR /code
RUN apt update
RUN apt install -y apcupsd
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./apcmqtt ./apcmqtt
CMD ["python", "-m", "apcmqtt", "-c", "/config/apcmqtt.yaml"]