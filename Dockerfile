FROM python:3.6-alpine

WORKDIR /app
ADD . .

RUN apk add --no-cache --virtual build \
      git \
      build-base \
      libffi-dev \
      openssl-dev \
      openssh && \
    apk add --no-cache \
      su-exec \
      libffi \
      libstdc++ && \
    adduser -D selene && \
    mkdir -p /root/.ssh && mv /app/docker_root/root/.ssh/id_rsa /root/.ssh/id_rsa && \
    chmod 0600 /root/.ssh/id_rsa && \
    ssh-keyscan git.bink.com > /root/.ssh/known_hosts && \
    ssh-keyscan gitlab.com >> /root/.ssh/known_hosts && \
    pip install pipenv gunicorn && \
    pipenv install --system --deploy --ignore-pipfile && \
    apk del --no-cache build

CMD ["/sbin/su-exec","selene","/usr/local/bin/gunicorn","-w 4","-b 0.0.0.0:9000","wsgi:app"]
