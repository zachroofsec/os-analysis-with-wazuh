#!/bin/bash

/init_scripts/wazuh.sh
/init_scripts/merlin.sh

tail -F /var/ossec/logs/ossec.log /var/log/merlin/merlin.log

