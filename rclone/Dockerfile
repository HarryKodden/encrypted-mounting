FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=rclone/rclone:latest /usr/local/bin/rclone /usr/local/bin/

WORKDIR /app

ADD app .

RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -y samba-vfs-modules fuse tzdata ca-certificates vim
RUN rm -rf /var/lib/apt/lists/* && apt-get clean

RUN echo "user_allow_other" >> /etc/fuse.conf

EXPOSE 80

CMD ["python", "app.py"]
