#!/usr/bin/python3
import logging
import subprocess
import sys
import os
import time

logging.basicConfig(level=logging.DEBUG, filename='/var/ossec/logs/deny-invisible-process.log', format='%(asctime)s %(levelname)s:%(message)s')
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

process = subprocess.run(["unhide", "quick"], capture_output=True, text=True)
hidden_pids = []
for line in process.stdout.splitlines():
    if 'found hidden pid:' in line.lower():
        # Strip out whitespace
        line = "".join(line.split())
        pid = line.split(':')[-1]
        logging.info(f"Killing Hidden Process: {pid}")
        process = subprocess.run(["kill", "-SIGKILL", pid], capture_output=True, text=True)