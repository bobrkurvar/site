FROM ubuntu:22.04 AS build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    pyinstaller \
    questionary

WORKDIR /src

COPY devops ./devops
COPY core ./core

RUN python3 -m PyInstaller \
    --clean \
    --onefile \
    --name devops \
    --paths /src \
    ./devops/__main_server__.py


FROM scratch

COPY --from=build /src/dist/devops /devops