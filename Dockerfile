FROM python:3.13-slim

WORKDIR /app

COPY . /app

RUN bash setup4host.sh

CMD ["/app/.env/bin/python", "main.py"]
