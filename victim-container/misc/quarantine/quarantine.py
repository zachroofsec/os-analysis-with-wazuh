#!/usr/bin/python3
import logging
import os
import subprocess
import sys
import time

logging.basicConfig(level=logging.DEBUG, filename='/var/ossec/logs/quarantine.log', format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


def ar_log():
    # Logging the AR request
    args_list = (' '.join(sys.argv[1:]))
    now = time.strftime("%a %b %d %H:%M:%S %Z %Y")
    msg = '{0} {1} {2}'.format(now, os.path.realpath(__file__), args_list)
    f = open('/var/ossec/logs/active-responses.log', 'a')
    f.write(msg + '\n')
    f.close()


ar_log()


class Quarantine:
    # def __init__(self):
    #     self._whitelisted_cidr = "8.8.8.8/32"

    @staticmethod
    def log_stdout_stderr(calling_process_name: str, process: subprocess.CompletedProcess):
        for line in process.stdout.splitlines():
            logger.info(f'{calling_process_name}: {line}')
        for line in process.stderr.splitlines():
            logger.error(f'{calling_process_name}: {line}')

    def set_default_egress_policy(self):
        calling_process_name = "ufw"
        process = subprocess.run([calling_process_name,
                                  "default", "deny", "outgoing"],
                                 capture_output=True,
                                 text=True,
                                 check=True)

        Quarantine.log_stdout_stderr(calling_process_name=calling_process_name, process=process)

    def set_default_ingress_policy(self):
        calling_process_name = "ufw"
        process = subprocess.run([calling_process_name,
                                  "default", "deny", "incoming"],
                                 capture_output=True,
                                 text=True,
                                 check=True)

        Quarantine.log_stdout_stderr(calling_process_name=calling_process_name, process=process)

    def set_egress_policy(self, cidr: str):
        calling_process_name = "ufw"
        process = subprocess.run([calling_process_name,
                                  "allow", "out", "to", cidr],
                                 capture_output=True,
                                 text=True,
                                 check=True)

        Quarantine.log_stdout_stderr(calling_process_name=calling_process_name, process=process)

    def set_ingress_policy(self, cidr: str):
        calling_process_name = "ufw"
        process = subprocess.run([calling_process_name,
                                  "allow", "from", cidr],
                                 capture_output=True,
                                 text=True,
                                 check=True)

        Quarantine.log_stdout_stderr(calling_process_name=calling_process_name, process=process)

    def enable(self):
        calling_process_name = "ufw"
        process = subprocess.run([calling_process_name,
                                  "enable"],
                                 capture_output=True,
                                 text=True,
                                 check=True)

        Quarantine.log_stdout_stderr(calling_process_name=calling_process_name, process=process)


quarantine = Quarantine()
quarantine.set_default_egress_policy()
quarantine.set_default_ingress_policy()
quarantine.set_egress_policy(cidr="8.8.8.8/32")
quarantine.set_ingress_policy(cidr="8.8.8.8/32")
quarantine.enable()
# enable command