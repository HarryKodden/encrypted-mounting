#!/bin/bash

RENEW=false
TOUCH=/etc/renewed

if [ -f "$TOUCH" ]; then
    for f in /etc/mounts/*.conf
    do
        if [ "$f" -nt "$TOUCH" ]; then
            RENEW=true
            break
        fi
    done
else
    RENEW=true
fi

if [ $RENEW = false ]; then 
    exit 0
fi

touch "$TOUCH"

NGINX=$(ps -ax|grep nginx|grep master|awk '{print $1;}')

kill -HUP $NGINX 

for f in /etc/mounts/*.conf
do 
    p=$(basename "$f" .conf)
    ln -sf /etc/mounts/$p /etc/pam.d/$p
done