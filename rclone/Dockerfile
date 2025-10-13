# rclone-ssh-project/Dockerfile

FROM alpine:3.16

ARG ROOT_PASSWORD=${RCLONE_ROOT_PASSWORD}
ENV RCLONE_CONFIG=/root/.config/rclone/rclone.conf

RUN apk add --no-cache rclone openssh bash

RUN ssh-keygen -A

RUN echo "root:${ROOT_PASSWORD}" | chpasswd
RUN mkdir -p /root/.config/rclone

COPY sshd_config /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
