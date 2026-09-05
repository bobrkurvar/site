FROM docker:29-cli

RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv

RUN python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir questionary

WORKDIR /app

COPY . ./devops

ENTRYPOINT ["python", "-m", "devops"]