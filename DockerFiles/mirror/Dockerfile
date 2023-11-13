# syntax = docker/dockerfile:1.4

FROM archlinux:latest

RUN pacman -Sy
RUN pacman -S --noconfirm python python-pip python-fastapi python-pydantic python-zstandard python-psycopg2 uvicorn libtorrent libtorrent-rasterbar

COPY ./pactor /app/pactor

WORKDIR /app

ENTRYPOINT /usr/bin/python -m pactor mirror --addr 0.0.0.0