#!/bin/bash

# Script should successfully run on Kali Linux 2020.3.0
#! Installs: docker, docker-compose, Wazuh Configuration

#! This script aims to replicate instructions from the Wazuh documentation:
# 1) https://documentation.wazuh.com/4.0/docker/docker-installation.html
# 2) https://documentation.wazuh.com/4.0/docker/wazuh-container.html

#! Recommendations
# 1) Docker host preferences: Give at least 6GB of memory to the docker daemon (the containers might not use it, but Elasticsearch will have issues without this minimum)

# Install Docker and misc dependencies
sudo apt-get update &&\
    sudo apt-get install -y docker.io &&\

#    Use docker through a non-root user
#     (You’ll have to log out (and back in) for this to take effect)
    sudo usermod -aG docker $USER || exit

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose &&\
    sudo chmod +x /usr/local/bin/docker-compose || exit

#! Set virtual memory for Elasticsearch container (used by Wazuh)
# If you don’t set max_map_count on your host, Elasticsearch will PROBABLY FAIL
sudo sysctl -w vm.max_map_count=262144

#! Allow iptables to be set within the Victim container
# (Needed for custom Wazuh Active Response script)
sudo modprobe ip6table_filter

echo "Installation Finished!"