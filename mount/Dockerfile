FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    nginx nginx-full wget cron curl vim libpam-dev libpam-python rsyslog locales

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8 
RUN apt-get install -y software-properties-common
RUN add-apt-repository universe
RUN apt-get install -y python2
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output /tmp/get-pip.py
RUN python2 /tmp/get-pip.py
RUN pip2 install requests

ADD proxy.conf /etc/nginx/proxy.conf
ADD conf.d /etc/nginx/conf.d
ADD vault-pam-wallet.py /usr/local/bin/

RUN rm -f /etc/nginx/conf.d/default.conf /etc/nginx/sites-enabled/*

COPY renew.sh /usr/local/bin/renew.sh
RUN chmod a+x /usr/local/bin/renew.sh

RUN echo "* * * * * root /usr/local/bin/renew.sh" >/etc/cron.d/renew

CMD [ "sh", "-c", "rsyslogd && cron && nginx -g 'daemon off;'" ]
