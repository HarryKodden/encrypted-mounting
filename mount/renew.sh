#!/bin/bash

RENEW=false
TOUCH=/etc/renewed

# In order to minimize overhead, we only renew if there are actual updates
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

# Remove broken links to no longer existing pam files...
find /etc/pam.d -xtype l -delete

# No updates, get out !
if [ $RENEW = false ]; then 
    exit 0
fi

touch "$TOUCH"

# Find master nginx process...
NGINX=$(ps -ax|grep nginx|grep master|awk '{print $1;}')

# Reload configurations...
kill -HUP $NGINX 

# Activate corresponding pam configurationsx
for f in /etc/mounts/*.pam
do 
    p=$(basename "$f" .pam)
    ln -sf $f /etc/pam.d/$p
done

# Done !