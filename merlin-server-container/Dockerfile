FROM ubuntu:20.04

ARG MERLIN_BASE_VERSION=v0.9.0-beta
ARG MERLIN_FILE_NAME=merlinServer-Linux-x64.7z

RUN apt-get update &&\
    apt-get install -y git \
        p7zip-full \
        vim \
        wget

RUN mkdir -p /opt/merlin /var/log/merlin
WORKDIR /opt/merlin
RUN wget https://github.com/Ne0nd0g/merlin/releases/download/${MERLIN_BASE_VERSION}/${MERLIN_FILE_NAME} &&\
    7za x -pmerlin ${MERLIN_FILE_NAME} &&\
    rm -rf "${MERLIN_FILE_NAME}"

COPY init_scripts/entrypoint.sh /entrypoint.sh
COPY init_scripts/merlin.sh /merlin.sh
COPY foothold /foothold

RUN chmod +x /entrypoint.sh /merlin.sh
CMD ["/entrypoint.sh"]
