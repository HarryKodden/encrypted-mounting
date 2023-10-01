FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    nginx nginx-full libnginx-mod-http-lua \
    wget cron curl vim git sudo \
    ca-certificates autoconf build-essential make \
    libpam-dev libcurl4-gnutls-dev libhiredis-dev libssl-dev \
    rsyslog locales pamtester

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8

RUN git clone https://github.com/HarryKodden/SRAM-Token-Service.git /pam && \
    cd /pam && \
    git clone https://github.com/json-parser/json-parser.git && \
    make install && \
    rm -rf /pam

ADD proxy.conf /etc/nginx/proxy.conf
ADD conf.d /etc/nginx/conf.d

RUN rm -f /etc/nginx/conf.d/default.conf /etc/nginx/sites-enabled/*

COPY renew.sh /usr/local/bin/renew.sh
RUN chmod a+x /usr/local/bin/renew.sh

RUN echo "* * * * * root /usr/local/bin/renew.sh" >/etc/cron.d/renew

CMD [ "sh", "-c", "rsyslogd && cron && nginx -g 'daemon off;'" ]