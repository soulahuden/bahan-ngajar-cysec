FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server \
        binutils \
        nano \
        less \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/run/sshd

COPY sshd_config /etc/ssh/sshd_config
COPY banner.txt /etc/ssh/banner.txt
COPY setup-levels.sh /usr/local/sbin/setup-levels.sh
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /usr/local/sbin/setup-levels.sh /entrypoint.sh \
    && /usr/local/sbin/setup-levels.sh

EXPOSE 22

CMD ["/entrypoint.sh"]
