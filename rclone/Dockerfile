FROM python:3.7

RUN apt-get update && \
    apt-get install -y samba-vfs-modules fuse tzdata ca-certificates vim && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=rclone/rclone:1.57 /usr/local/bin/rclone /usr/local/bin/

WORKDIR /app

ADD app .

RUN pip install -r requirements.txt
RUN echo "user_allow_other" >> /etc/fuse.conf

EXPOSE 80

CMD ["python", "app.py"]
