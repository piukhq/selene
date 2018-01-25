FROM ubuntu:xenial
MAINTAINER Chris Pressland <cp@bink.com>

ADD . /usr/local/src/selene

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN addgroup --gid 1550 apps && \
 adduser --system --no-create-home --uid 1550 --gid 1550 apps && \
 echo "deb http://ppa.launchpad.net/nginx/stable/ubuntu xenial main" >> /etc/apt/sources.list && \
 echo "deb-src http://ppa.launchpad.net/nginx/stable/ubuntu xenial main" >> /etc/apt/sources.list && \
 apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C300EE8C && \
 apt-get update && \
 apt-get -y install rsync git git-core python3 python3-pip python3-dev libpq-dev nginx curl lftp locales&& \
 curl -L 'https://github.com/just-containers/s6-overlay/releases/download/v1.18.1.5/s6-overlay-amd64.tar.gz' -o /tmp/s6-overlay-amd64.tar.gz && \
 tar xzf /tmp/s6-overlay-amd64.tar.gz -C / && \
 sed -i -e 's/user www-data;/user apps;/g' /etc/nginx/nginx.conf && \
 rm -rf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default && \
 rsync -a --remove-source-files /usr/local/src/selene/docker_root/ / && \
 chmod 600 /root/.ssh/id_rsa && \
 chmod 600 /root/.ssh/config && \
 pip3 install --upgrade pip && \
 pip3 install uwsgi pipenv && \
 cd /usr/local/src/selene && \
 pipenv install --deploy --system && \
 chown apps:apps /usr/local/src -R && \
 locale-gen en_GB.UTF-8 && \
 apt-get -y remove rsync git git-core curl && \
 apt-get -y autoremove && \
 apt-get clean && \
 rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV LANG=en_GB.UTF-8 \
    LANGUAGE=en_GB:en \
    LC_ALL=en_GB.UTF-8

ENTRYPOINT ["/init"]
