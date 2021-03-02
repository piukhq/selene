FROM binkhq/python:3.8

WORKDIR /app
ADD . .

RUN apt update && apt -y install git && \
    mkdir -p /root/.ssh && chown 700 /root/.ssh && \
    mv /app/docker_root/root/.ssh/id_rsa /root/.ssh && \
    chown 600 /root/.ssh/id_rsa && \
    ssh-keyscan git.bink.com > /root/.ssh/known_hosts && \
    pip install pipenv gunicorn && \
    pipenv install --system --deploy --ignore-pipfile && \
    rm -rf /root/.ssh /app/docker_root && \
    apt -y autoremove git && rm -rf /var/lib/apt/lists/*

CMD ["/usr/local/bin/gunicorn","-w 4","-b 0.0.0.0:9000","wsgi:app"]
