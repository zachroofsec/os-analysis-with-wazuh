FROM ubuntu:20.04

ARG MERLIN_BASE_VERSION=v0.9.0-beta
ARG MERLIN_FILE_NAME=merlinAgent-Linux-x64.7z
ARG WAZUH_VERSION=4.0.0-1

RUN apt-get update &&\
    apt-get install -y wget \
        software-properties-common &&\
    wget -qO-  https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add - &&\
    echo "deb https://packages.wazuh.com/4.x/apt/ stable main" | tee /etc/apt/sources.list.d/wazuh.list &&\
    apt-get update &&\
    apt-get install -y \
        # vim is needed for general debugging
        vim \
        # netcat is needed for merlin.sh
        netcat \
        # p7zip is needed to unzip Merlin (see below)
        p7zip-full \
        wazuh-agent \
        # unhide is needed for deny-invisible-process.py
        unhide \
        # gcc is needed for foothold.py
        gcc \
        # net-tools is needed to run `netstat`
        net-tools \
        # ufw is needed for quarantine.py
        ufw \
        # iputils-ping is needed to run `ping`
        iputils-ping &&\
    apt-get update

RUN mkdir -p /opt/merlin /var/log/merlin
WORKDIR /opt/merlin
RUN wget https://github.com/Ne0nd0g/merlin/releases/download/${MERLIN_BASE_VERSION}/${MERLIN_FILE_NAME} &&\
    7za x -pmerlin ${MERLIN_FILE_NAME} &&\
    rm -rf "${MERLIN_FILE_NAME}"

COPY /init_scripts/ /init_scripts/
RUN chmod +x /init_scripts/*

COPY /misc/deny-invisible-process/deny-invisible-process.py /var/ossec/active-response/bin/deny-invisible-process.py
RUN chmod +x /var/ossec/active-response/bin/deny-invisible-process.py

COPY /misc/quarantine/quarantine.py /var/ossec/active-response/bin/quarantine.py
RUN chmod +x /var/ossec/active-response/bin/quarantine.py

COPY /misc/ossec.conf /var/ossec/etc/ossec.conf

COPY /misc/ /tmp/

ENTRYPOINT ["/init_scripts/entrypoint.sh"]