FROM python:3.6

WORKDIR /app
ADD . .

ENV PIP_NO_BINARY="psycopg2"

RUN mkdir -p /root/.ssh && mv /app/docker_root/root/.ssh/id_rsa /root/.ssh/id_rsa && \
    chmod 0600 /root/.ssh/id_rsa && \
    ssh-keyscan git.bink.com > /root/.ssh/known_hosts && \
    pip install --upgrade pip && pip install pipenv uwsgi && \
    pipenv install --system --deploy
